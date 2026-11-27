"""Replay the matched comparison's pre-camera XYZ samples."""
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
T=2*math.pi
BASE=dict(format='vortex-threads-xyz-v1',frames=240,flow_time=4.2,nu=.13,seed=117,latitude_loops=34,meridian_loops=25,spirals=12,samples_per_thread=141,tracers=204)
def generate(spec):
    if spec.keys()!=BASE.keys() or any(type(spec[k])!=type(v) or (spec[k]!=v and k!='seed') for k,v in BASE.items()) or not 0<=spec['seed']<2**32:
        raise ValueError('unsupported version or parameters')
    n=spec['frames']; tf=spec['flow_time']; nu=spec['nu']
    u=np.linspace(0,T,spec['samples_per_thread'])
    curves=[]
    for h in np.linspace(0,T,spec['latitude_loops'],endpoint=False): curves.append(np.stack((u,np.full_like(u,h)),axis=1))
    for h in np.linspace(0,T,spec['meridian_loops'],endpoint=False): curves.append(np.stack((np.full_like(u,h),u),axis=1))
    for h in np.linspace(0,T,spec['spirals'],endpoint=False): curves.append(np.stack(((u+h)%T,(2*u+h*.24)%T),axis=1))
    points=np.stack(curves)
    seeds=np.random.default_rng(spec['seed']).uniform(0,T,(spec['tracers'],2))
    dt=tf/(n-1)
    def ease(lo,hi,s):
        s=min(max((s-lo)/(hi-lo),0),1)
        return s*s*(3-2*s)
    def shape(z,s):
        x,y=z[...,0],z[...,1]
        squash=ease(.12,.42,s); b=ease(.40,.83,s)
        rho=(1-b)*(1.04+.20*squash)*np.abs(np.cos(y))+b*(1.03+.49*np.cos(y))
        h=((1-b)*(1.04-.56*squash)+b*.45)*np.sin(y)
        return rho*np.cos(x),rho*np.sin(x),h
    def rhs(z,t):
        x,y=z[...,0],z[...,1]
        return np.exp(-2*nu*t)*np.stack((np.cos(x)*np.sin(y),-np.sin(x)*np.cos(y)),axis=-1)
    def step(z,t):
        k1=rhs(z,t); k2=rhs(z+dt*k1/2,t+dt/2)
        k3=rhs(z+dt*k2/2,t+dt/2); k4=rhs(z+dt*k3,t+dt)
        return (z+dt*(k1+k2*2+k3*2+k4)/6)%T
    for i in range(n):
        s=i/(n-1);t=i*dt
        for surface_s in (0,s):
            for group in (points,seeds):
                yield np.asarray(np.stack(shape(group,surface_s),axis=-1),dtype='<f8',order='C').tobytes()
        points=step(points,t); seeds=step(seeds,t)
def main():
    p=argparse.ArgumentParser()
    p.add_argument('recipe',type=Path); p.add_argument('--output',type=Path)
    p.add_argument('--expect')
    a=p.parse_args()
    spec=json.loads(a.recipe.read_text())
    h=hashlib.sha256(); size=0
    if a.output:
        with a.output.open('xb') as f:
            for data in generate(spec): f.write(data); h.update(data); size+=len(data)
    else:
        for data in generate(spec): h.update(data); size+=len(data)
    if a.expect and h.hexdigest()!=a.expect.lower(): p.exit(1,'SHA-256 mismatch\n')
    print(f'{size} bytes   sha256 {h.hexdigest()}')
if __name__=='__main__': main()
