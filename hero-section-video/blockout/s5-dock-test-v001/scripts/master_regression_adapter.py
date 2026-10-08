import bpy,sys,runpy,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--test',required=True);p.add_argument('--scene',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);bpy.context.window.scene=bpy.data.scenes[a.scene];runpy.run_path(a.test,run_name='__main__')
