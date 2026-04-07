# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

visualization/periodic_3d.py — Interactive 3D periodic table coloured by F_element.
V02: 3D bar chart. X=period, Y=group, Z=F_element (bar height).
Green=high F, Red=low F. Noble gases visually dominant.
Uses Plotly (no matplotlib 3D). Exports HTML + JSON.
"""
from __future__ import annotations
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'../../..'))
from freedom_physics.elements.periodic_table import PERIODIC_TABLE

def generate_periodic_3d_data(channel: str = "electrical") -> list[dict]:
    """
    Compute visualization data for all 118 elements.
    Returns list of {sym, Z, period, group, F, color_hex} dicts.
    """
    channel_fns = {
        "electrical": lambda el: el.F_electrical(),
        "thermal":    lambda el: el.F_thermal(),
        "chemical":   lambda el: el.F_chemical(),
        "nuclear":    lambda el: el.F_nuclear(),
        "ionize":     lambda el: el.F_ionize(),
        "structural": lambda el: el.F_structural(),
    }
    fn = channel_fns.get(channel, channel_fns["electrical"])

    def f_to_hex(F: float) -> str:
        t = max(0.0, min(1.0, F))
        # Green-to-Red: high F=green, low F=red
        r = int(220*(1-t)+40*t)
        g = int(40*(1-t)+200*t)
        b = 60
        return f"#{r:02x}{g:02x}{b:02x}"

    result = []
    for sym, el in PERIODIC_TABLE.items():
        if el.group is None:
            continue
        F = fn(el)
        result.append({
            "sym":    sym,
            "name":   el.name,
            "Z":      el.Z,
            "period": el.period,
            "group":  el.group,
            "block":  el.block,
            "F":      round(F, 4),
            "color":  f_to_hex(F),
        })
    return sorted(result, key=lambda x: x["Z"])

def export_html(channel: str = "electrical",
                output_path: str = "/tmp/periodic_3d.html") -> str:
    """
    Export interactive 3D periodic table as HTML.
    Noble gases (group 18) must be visually prominent on F_chemical=0 but high F_ionize.
    """
    data = generate_periodic_3d_data(channel)
    # Build embedded-data HTML (no server required, pure browser)
    data_json = json.dumps(data)
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<title>Periodic Table as Freedom Landscape — F=P/D SIMULATED</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<style>
body{{margin:0;background:#fff;font-family:sans-serif;}}
#info{{position:fixed;top:12px;left:12px;background:rgba(255,255,255,0.9);
       padding:8px 14px;border-radius:8px;font-size:13px;border:0.5px solid #e5e7eb;}}
#canvas{{display:block;}}
</style>
</head>
<body>
<div id="info">
  <b>F = P / D — Periodic Table</b><br>
  Channel: <b>{channel}</b><br>
  Height = F value · Green=high F · Red=low F<br>
  <small>SIMULATED · F=P/D HYPOTHESIS UNDER TEST · seed=2026</small>
</div>
<canvas id="canvas"></canvas>
<script>
const DATA = {data_json};
const canvas = document.getElementById('canvas');
const renderer = new THREE.WebGLRenderer({{canvas,antialias:true}});
renderer.setSize(window.innerWidth,window.innerHeight);
renderer.setClearColor(0xffffff,1);
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xffffff,40,70);
const cam = new THREE.PerspectiveCamera(42,window.innerWidth/window.innerHeight,0.1,200);
let theta=0.6,phi=0.75;
function setcam(){{
  const R=35;
  cam.position.set(R*Math.sin(phi)*Math.cos(theta),R*Math.cos(phi),R*Math.sin(phi)*Math.sin(theta));
  cam.lookAt(9,0,3);
}}
setcam();
scene.add(new THREE.AmbientLight(0xffffff,0.5));
const dl=new THREE.DirectionalLight(0xfff5e0,0.8);dl.position.set(10,15,8);scene.add(dl);
const BW=0.82,BG=0.16,FS=4.0;
DATA.forEach(el=>{{
  const F=Math.max(el.F,0.005);
  const h=F*FS;
  const geo=new THREE.BoxGeometry(BW,h,BW);
  const col=new THREE.Color(el.color);
  const mesh=new THREE.Mesh(geo,new THREE.MeshPhongMaterial({{color:col,shininess:20}}));
  mesh.position.set((el.group-1)*(BW+BG),h/2,(el.period-1)*(BW+BG));
  scene.add(mesh);
}});
let auto=true,lx=0,ly=0,drag=false;
canvas.addEventListener('mousedown',e=>{{drag=true;auto=false;lx=e.clientX;ly=e.clientY;}});
canvas.addEventListener('mousemove',e=>{{
  if(!drag)return;
  theta-=(e.clientX-lx)*0.008;phi=Math.max(0.15,Math.min(1.5,phi+(e.clientY-ly)*0.008));
  lx=e.clientX;ly=e.clientY;setcam();
}});
canvas.addEventListener('mouseup',()=>drag=false);
window.addEventListener('resize',()=>{{
  renderer.setSize(window.innerWidth,window.innerHeight);
  cam.aspect=window.innerWidth/window.innerHeight;cam.updateProjectionMatrix();
}});
function animate(){{
  requestAnimationFrame(animate);
  if(auto){{theta+=0.003;setcam();}}
  renderer.render(scene,cam);
}}
animate();
</script>
</body></html>"""
    with open(output_path,'w') as f:
        f.write(html)
    return output_path
