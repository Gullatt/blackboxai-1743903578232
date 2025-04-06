from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import requests
import ssl
from datetime import datetime
from typing import Optional
import pdfkit

app = FastAPI(title="SentinelX API", description="API de análise de segurança digital")

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    target: str
    scan_type: Optional[str] = "basic"

class AnalysisResult(BaseModel):
    target: str
    scan_date: str
    ports: list
    headers: dict
    ssl_info: dict
    risk_level: str
    explanations: list
    recommendations: list

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_security(request: AnalysisRequest):
    """Endpoint principal para análise de segurança"""
    try:
        # Validação básica do target
        if not (request.target.startswith('http') or request.target.replace('.','').isdigit()):
            raise HTTPException(status_code=400, detail="URL ou IP inválido")

        result = {
            "target": request.target,
            "scan_date": datetime.now().isoformat(),
            "ports": scan_ports(request.target),
            "headers": check_headers(request.target),
            "ssl_info": check_ssl(request.target),
        }

        # Classificação de risco e explicações
        risk_data = assess_risk(result)
        result.update(risk_data)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def scan_ports(target: str) -> list:
    """Verifica portas abertas usando nmap"""
    try:
        # Remove protocolo se presente
        clean_target = target.replace('https://', '').replace('http://', '').split('/')[0]
        
        # Executa nmap básico (requer nmap instalado)
        cmd = f"nmap -F {clean_target}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Processa resultado
        open_ports = []
        for line in result.stdout.split('\n'):
            if 'open' in line:
                parts = line.split()
                open_ports.append({
                    "port": parts[0],
                    "service": parts[2],
                    "status": "open"
                })
        
        return open_ports

    except Exception:
        return []

def check_headers(target: str) -> dict:
    """Verifica headers de segurança HTTP"""
    try:
        if not target.startswith('http'):
            target = f"http://{target}"
        
        response = requests.get(target, timeout=10)
        headers = {
            "hsts": response.headers.get('Strict-Transport-Security'),
            "csp": response.headers.get('Content-Security-Policy'),
            "xss_protection": response.headers.get('X-XSS-Protection'),
            "content_type": response.headers.get('Content-Type'),
            "server": response.headers.get('Server')
        }
        return headers

    except Exception:
        return {}

def check_ssl(target: str) -> dict:
    """Verifica certificado SSL"""
    try:
        if not target.startswith('http'):
            target = f"https://{target}"
        
        hostname = target.replace('https://', '').split('/')[0]
        context = ssl.create_default_context()
        
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Validade do certificado
                not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (not_after - datetime.now()).days
                
                return {
                    "issuer": cert['issuer'][0][0][1],
                    "valid_until": cert['notAfter'],
                    "days_remaining": days_left,
                    "subject": cert['subject'][0][0][1]
                }

    except Exception:
        return {}

def assess_risk(data: dict) -> dict:
    """Classifica riscos e gera explicações"""
    risk_score = 0
    explanations = []
    recommendations = []
    
    # Análise de portas
    if data['ports']:
        risk_score += len(data['ports']) * 5
        explanations.append(f"Encontradas {len(data['ports'])} portas abertas")
        recommendations.append("Considere fechar portas não essenciais")
    
    # Análise de headers
    if not data['headers'].get('hsts'):
        risk_score += 10
        explanations.append("Falta header HSTS (proteção contra downgrade HTTPS)")
        recommendations.append("Implemente HSTS para forçar conexões seguras")
    
    # Análise SSL
    if not data['ssl_info']:
        risk_score += 20
        explanations.append("Sem certificado SSL válido")
        recommendations.append("Obtenha um certificado SSL válido")
    elif data['ssl_info'].get('days_remaining', 0) < 30:
        risk_score += 5
        explanations.append(f"Certificado SSL expira em {data['ssl_info']['days_remaining']} dias")
        recommendations.append("Renove o certificado SSL antes da expiração")
    
    # Classificação final
    if risk_score >= 30:
        risk_level = "🔴 Alto"
    elif risk_score >= 15:
        risk_level = "🟡 Médio"
    else:
        risk_level = "🟢 Baixo"
    
    return {
        "risk_level": risk_level,
        "explanations": explanations,
        "recommendations": recommendations
    }

@app.get("/report")
async def generate_report(target: str):
    """Gera relatório PDF"""
    try:
        analysis = await analyze_security(AnalysisRequest(target=target))
        
        # HTML template para PDF
        html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial; margin: 2cm; }}
                    h1 {{ color: #2B6CB0; }}
                    .risk-high {{ color: red; }}
                    .risk-medium {{ color: orange; }}
                    .risk-low {{ color: green; }}
                </style>
            </head>
            <body>
                <h1>Relatório de Segurança SentinelX</h1>
                <h2>Análise de: {analysis['target']}</h2>
                <p>Data: {analysis['scan_date']}</p>
                
                <h3>Nível de Risco: <span class="risk-{analysis['risk_level'].lower()}">
                    {analysis['risk_level']}
                </span></h3>
                
                <h4>Detalhes Técnicos:</h4>
                <ul>
                    {''.join(f'<li>{item}</li>' for item in analysis['explanations'])}
                </ul>
                
                <h4>Recomendações:</h4>
                <ul>
                    {''.join(f'<li>{item}</li>' for item in analysis['recommendations'])}
                </ul>
                
                <footer>
                    <p>Ferramenta educativa. Para ações técnicas, consulte um profissional.</p>
                </footer>
            </body>
        </html>
        """
        
        # Configuração do PDFkit (requer wkhtmltopdf instalado)
        pdf = pdfkit.from_string(html, False)
        
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=relatorio_{target}.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)