# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

visualization/freedom_field_3d.py — 3D volumetric F=P/D field.
V01: colored isosurface. Exports HTML + data JSON.
"""
from __future__ import annotations
import json, math

def compute_freedom_field(nx:int=30, ny:int=30, nz:int=30,
                          P_center:float=0.8, D_gradient_scale:float=2.0) -> dict:
    """
    Compute F=P/D field on a 3D grid.
    P varies spatially (observer perception). D varies as gradient.
    Returns: {x,y,z,F} lists for visualization.
    """
    from freedom_physics.core.freedom import compute_F
    xs,ys,zs,Fs=[],[],[],[]
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                x=i/(nx-1); y=j/(ny-1); z=k/(nz-1)
                # P decreases from center (observer at center has max perception)
                dist=math.sqrt((x-0.5)**2+(y-0.5)**2+(z-0.5)**2)
                P=P_center*(1-dist)
                # D increases toward corners (crystallized distortion at periphery)
                D=1.0+D_gradient_scale*dist**2
                F=compute_F(max(P,0.01),D)
                xs.append(round(x,3)); ys.append(round(y,3))
                zs.append(round(z,3)); Fs.append(round(F,4))
    return {"x":xs,"y":ys,"z":zs,"F":Fs,"n_points":len(Fs),
            "label":"SIMULATED","thesis":"T2"}

def export_html(output_path:str="/tmp/freedom_field_3d.html") -> str:
    data = compute_freedom_field(15,15,15)  # smaller for embed
    data_json=json.dumps({"x":data["x"][:1000],"y":data["y"][:1000],
                          "z":data["z"][:1000],"F":data["F"][:1000]})
    html=f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>3D Freedom Field F=P/D — SIMULATED</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head><body style="margin:0;background:#fff">
<canvas id="c"></canvas>
<script>
const D={data_json};
const canvas=document.getElementById('c');
const renderer=new THREE.WebGLRenderer({{canvas,antialias:true}});
renderer.setSize(window.innerWidth,window.innerHeight);
renderer.setClearColor(0xffffff,1);
const scene=new THREE.Scene();
const cam=new THREE.PerspectiveCamera(45,window.innerWidth/window.innerHeight,0.1,100);
cam.position.set(2,1.5,2);cam.lookAt(0.5,0.5,0.5);
scene.add(new THREE.AmbientLight(0xffffff,0.6));
scene.add(Object.assign(new THREE.DirectionalLight(0xffeedd,0.8),{{position:{{x:2,y:3,z:2}}}});
D.F.forEach((F,i)=>{{
  const geo=new THREE.SphereGeometry(0.02,6,6);
  const t=F;
  const col=new THREE.Color(1-t,t*0.8,0.1);
  const mesh=new THREE.Mesh(geo,new THREE.MeshPhongMaterial({{color:col}}));
  mesh.position.set(D.x[i],D.y[i],D.z[i]);
  if(F>0.3)scene.add(mesh);
}});
let t=0;
function animate(){{requestAnimationFrame(animate);t+=0.005;
  cam.position.set(2*Math.cos(t),1.5,2*Math.sin(t));cam.lookAt(0.5,0.5,0.5);
  renderer.render(scene,cam);}};animate();
</script></body></html>"""
    with open(output_path,'w') as f: f.write(html)
    return output_path
