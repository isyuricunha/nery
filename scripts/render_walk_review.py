"""Compare real locomotion GIFs with the unchanged reference-state GIFs."""
from pathlib import Path
import base64

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'pet/preview'

def render_review():
    cards=[('Repouso · referência',OUT/'web-idle.gif'),
           ('Aceno · referência',OUT/'web-waving.gif'),
           ('Esperando · referência',OUT/'web-waiting.gif'),
           ('Caminhada anterior',ROOT/'pet/candidates/walk-proportions/previous.gif'),
           ('Caminhada nova · esquerda',OUT/'web-running-left.gif'),
           ('Caminhada nova · direita',OUT/'web-running-right.gif')]
    html='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nery · Revisão da caminhada</title><style>body{margin:0;background:#181210;color:#f0e9e3;font:15px system-ui;line-height:1.5}main{max-width:1050px;padding:30px 20px;margin:auto}h1{font-size:27px;margin:0}p{color:#b9a195}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}figure{margin:0;background:#211915;border:1px solid #574035;border-radius:10px;padding:16px 8px;text-align:center}figure.new{border-color:#cc785c}figcaption{margin-bottom:12px}img{display:block;width:192px;height:208px;max-width:100%;object-fit:contain;margin:auto}a{color:#e1aa90}@media(max-width:650px){.grid{grid-template-columns:repeat(2,1fr)}figcaption{font-size:12px}}@media(max-width:390px){.grid{grid-template-columns:1fr}}</style><main><h1>Nery · Caminhada e estados de referência</h1><p>GIFs em reprodução contínua, na velocidade normal. Corpo e traço seguem os estados existentes; a caminhada mantém a proporção chibi arredondada.</p><div class="grid">'''
    for i,(title,path) in enumerate(cards):
        uri='data:image/gif;base64,'+base64.b64encode(path.read_bytes()).decode()
        html+=f'<figure class="{"new" if i>=4 else "reference"}"><figcaption>{title}</figcaption><img src="{uri}" alt="{title}" width="192" height="208"></figure>'
    html+='</div><p>Somente as duas direções da caminhada foram refeitas nesta revisão. Os sete outros estados, incluindo Failed, mantêm exatamente seus desenhos salvos.</p><p><a href="motion-review.html">Câmera lenta e avanço quadro a quadro →</a></p></main></html>'
    (OUT/'walk-review.html').write_text(html,encoding='utf-8')

if __name__=='__main__':
    render_review()
