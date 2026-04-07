import sys, os
# Force afi to be the primary freedom_physics package
afi_path = os.path.dirname(__file__)
lof_path = '/home/claude/lof'
# Remove lof from path if present, put afi first
for p in [lof_path, afi_path+'/freedom_physics']:
    if p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, afi_path)
