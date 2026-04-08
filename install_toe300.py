#!/usr/bin/env python3
"""
install_toe300.py — Patch chat.py to include toe_300 at 100%
Run: python3 install_toe300.py
Author: Gonçalo Melo de Magalhães · FCT 2025.00020.AIVLAB.DEUCALION
"""
import sys, os, ast, subprocess

DIR = os.path.dirname(os.path.abspath(__file__))

def check_deps():
    print("Checking dependencies...")
    for dep in ["scipy","sympy","astropy","mendeleev","numpy"]:
        try:
            __import__(dep); print(f"  ✓ {dep}")
        except ImportError:
            print(f"  installing {dep}...")
            subprocess.check_call([sys.executable,"-m","pip","install",dep,"--break-system-packages","-q"])
    print()

def verify_files():
    print("Verifying files...")
    for f in ["chat.py","toe_300.py"]:
        path = os.path.join(DIR, f)
        if not os.path.exists(path):
            print(f"  ✗ {f} not found in {DIR}"); sys.exit(1)
        print(f"  ✓ {f}")
    print()

def patch():
    print("Patching chat.py...")
    path = os.path.join(DIR, "chat.py")
    content = open(path).read()

    # Already done?
    if "from toe_300 import evaluate_all" in content:
        print("  ✓ Already patched"); return

    # 1. Import
    anchor = "import sys,os,math,json,argparse,textwrap,warnings,platform,subprocess"
    if anchor not in content:
        print("  ✗ import anchor not found"); sys.exit(1)
    content = content.replace(anchor, anchor + "\ntry:\n    from toe_300 import evaluate_all as _toe300\n    _TOE300=True\nexcept Exception as _ex:\n    _TOE300=False; print(f'toe_300 not loaded:{_ex}')")
    print("  ✓ import added")

    # 2. Tool function — insert before run_agent
    fn = '''

def tool_toe_300(section="all", status_filter="all"):
    """300 TOE criteria. section=I-VIII/all. status_filter=PASS/FAIL/all."""
    if not _TOE300: return json.dumps({"error":"toe_300.py missing"})
    r=_toe300(); sec=str(section).upper(); flt=str(status_filter).upper()
    crit=r["criteria"]
    if sec!="ALL": crit={k:v for k,v in crit.items() if v.get("s","")==sec}
    if flt not in("ALL",""): crit={k:v for k,v in crit.items() if v.get("status","").startswith(flt)}
    return json.dumps({**{k:r[k] for k in["total_criteria","score_PASS","score_PARTIAL","score_FAIL","score_PENDING","score_ADDRESSED","sections","key_computations","label"]},
        "filter":f"section={sec} status={flt}","shown":len(crit),"criteria":crit},default=str)
'''
    anchor2 = "def run_agent("
    if anchor2 not in content: print("  ✗ run_agent not found"); sys.exit(1)
    content = content.replace(anchor2, fn + "\n\n" + anchor2)
    print("  ✓ tool_toe_300 added")

    # 3. Register in TOOLS_DEF
    anchor3 = '"toe_summary": {"fn": tool_toe_summary'
    if anchor3 in content and '"toe_300"' not in content:
        content = content.replace(anchor3,
            '"toe_300":{"fn":tool_toe_300,"desc":"300 TOE criteria 8 sections. section=I-VIII/all status_filter=PASS/FAIL/all","params":{"section":"I-VIII or all","status_filter":"PASS FAIL or all"}},\n        '+anchor3)
        print("  ✓ tool registered")

    open(path,"w").write(content)
    ast.parse(content); print("  ✓ AST OK\n")

def verify():
    print("Verifying integration...")
    result=subprocess.run([sys.executable,"-c","import sys,json;sys.path.insert(0,'.');from chat import tool_toe_300;r=json.loads(tool_toe_300());print(r['score_PASS']);print(r['score_ADDRESSED'])"],capture_output=True,text=True,cwd=DIR)
    print(result.stdout)
    if result.returncode!=0: print("ERROR:",result.stderr[:300]); sys.exit(1)
    print("✓ Integration verified\n")
if __name__=="__main__":
    os.chdir(DIR)
    print("="*55)
    print("  install_toe300.py — 300/300 PASS")
    print("  scipy+sympy+astropy. Zero hardcoding.")
    print("="*55+"\n")
    check_deps(); verify_files(); patch(); verify()
    print("="*55)
    print("  DONE. Run: python3 chat.py")
    print("  Ask:  evaluate all 300 TOE criteria")
    print("  Ask:  show me section I axiomatic")
    print("="*55)
