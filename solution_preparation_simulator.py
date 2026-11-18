"""Chemical solution preparation calculator. Run: streamlit run solution_preparation_simulator.py"""
import re
import csv
from io import StringIO
import pandas as pd
import streamlit as st

ATOMIC = {
'H':1.008,'Li':6.94,'Be':9.0122,'B':10.81,'C':12.011,'N':14.007,'O':15.999,'F':18.998,'Na':22.98977,'Mg':24.305,'Al':26.98154,'Si':28.085,'P':30.97376,'S':32.06,'Cl':35.45,'K':39.0983,'Ca':40.078,'Sc':44.9559,'Ti':47.867,'V':50.9415,'Cr':51.9961,'Mn':54.938,'Fe':55.845,'Co':58.9332,'Ni':58.6934,'Cu':63.546,'Zn':65.38,'Ga':69.723,'Ge':72.630,'As':74.9216,'Se':78.971,'Br':79.904,'Rb':85.4678,'Sr':87.62,'Y':88.9058,'Zr':91.224,'Nb':92.9064,'Mo':95.95,'Ag':107.8682,'Cd':112.414,'In':114.818,'Sn':118.710,'Sb':121.760,'I':126.9045,'Cs':132.9055,'Ba':137.327,'La':138.9055,'Ce':140.116,'Pr':140.9077,'Nd':144.242,'Sm':150.36,'Eu':151.964,'Gd':157.25,'Tb':158.9254,'Dy':162.500,'Ho':164.9303,'Er':167.259,'Tm':168.9342,'Yb':173.045,'Lu':174.9668,'Hf':178.49,'Ta':180.9479,'W':183.84,'Pt':195.084,'Au':196.9666,'Hg':200.592,'Pb':207.2,'Bi':208.9804,'U':238.0289}
SALTS = {
'Fe':['FeCl3·6H2O','FeCl2·4H2O','Fe(NO3)3·9H2O','FeSO4·7H2O','Fe2(SO4)3'],
'Ni':['NiSO4·6H2O','NiCl2·6H2O','Ni(NO3)2·6H2O'],
'Co':['CoCl2·6H2O','CoSO4·7H2O','Co(NO3)2·6H2O'],
'Gd':['Gd(NO3)3·6H2O','GdCl3·6H2O','Gd2(SO4)3·8H2O'],
'Nd':['Nd(NO3)3·6H2O','NdCl3·6H2O','Nd2(SO4)3·8H2O'],
'Dy':['Dy(NO3)3·5H2O','DyCl3·6H2O'],
'La':['La(NO3)3·6H2O','LaCl3·7H2O'],
'Mn':['MnSO4·H2O','MnCl2·4H2O','Mn(NO3)2·4H2O'],
'Zn':['ZnSO4·7H2O','ZnCl2','Zn(NO3)2·6H2O'],
'Cu':['CuSO4·5H2O','CuCl2·2H2O','Cu(NO3)2·3H2O'],
'Al':['Al(NO3)3·9H2O','AlCl3·6H2O','Al2(SO4)3·18H2O'],
'Ce':['Ce(NO3)3·6H2O','CeCl3·7H2O'],
'Sm':['Sm(NO3)3·6H2O','SmCl3·6H2O'],
'Eu':['Eu(NO3)3·6H2O','EuCl3·6H2O'],
'Ca':['CaCl2·2H2O','Ca(NO3)2·4H2O'],
'Mg':['MgCl2·6H2O','MgSO4·7H2O'],
}

def parse_formula(formula):
    """Return element counts; supports nested parentheses and dot hydration."""
    formula = formula.replace(' ','').replace('·','.').replace('∙','.').replace('⋅','.')
    if not formula: raise ValueError('Enter a chemical formula.')
    total = {}
    for part in formula.split('.'):
        if not part: raise ValueError('Invalid hydration separator.')
        match = re.match(r'^(\d+)(.*)$',part)
        multiplier = int(match.group(1)) if match else 1
        part = match.group(2) if match else part
        tokens = re.findall(r'[A-Z][a-z]?|\d+|[()]',part)
        if ''.join(tokens) != part: raise ValueError(f'Unrecognized formula: {part}')
        pos = 0
        def group():
            nonlocal pos
            counts = {}
            while pos < len(tokens) and tokens[pos] != ')':
                tok = tokens[pos]; pos += 1
                if tok == '(':
                    nested = group()
                    if pos >= len(tokens) or tokens[pos] != ')': raise ValueError('Unmatched parenthesis.')
                    pos += 1
                elif tok in ATOMIC:
                    nested = {tok:1}
                else:
                    raise ValueError(f'Unexpected token: {tok}')
                n = 1
                if pos < len(tokens) and tokens[pos].isdigit():
                    n = int(tokens[pos]); pos += 1
                for k,v in nested.items(): counts[k] = counts.get(k,0)+v*n
            return counts
        result = group()
        if pos != len(tokens): raise ValueError('Unmatched closing parenthesis.')
        for k,v in result.items(): total[k] = total.get(k,0)+v*multiplier
    return total

def calculate(element, ppm, volume_ml, formula, purity_percent=100):
    counts = parse_formula(formula)
    if element not in counts: raise ValueError(f'{formula} does not contain {element}.')
    if not 0 < purity_percent <= 100: raise ValueError('Purity must be >0 and ≤100%.')
    if ppm < 0 or volume_ml <= 0: raise ValueError('Concentration must be ≥0 and volume >0.')
    mw = sum(ATOMIC[k]*v for k,v in counts.items())
    metal_mg = ppm*volume_ml/1000
    salt_mg = metal_mg*mw/(counts[element]*ATOMIC[element])/(purity_percent/100)
    return mw, metal_mg, salt_mg

st.set_page_config(page_title='Solution Preparation Simulator',page_icon='⚗️',layout='wide')
st.title('⚗️ Chemical Solution Preparation Simulator')
st.caption('Target concentrations are mg of ELEMENT per liter of FINAL solution (ppm for dilute aqueous solutions).')
volume = st.number_input('Final solution volume (mL)',min_value=0.001,value=250.0,step=50.0,format='%.3f')
if 'rows' not in st.session_state:
    st.session_state.rows = [dict(element=e,ppm=100.0,formula=SALTS[e][0],purity=100.0) for e in ['Fe','Ni','Co','Gd']]

c1,c2 = st.columns([1,4])
with c1:
    if st.button('➕ Add element',use_container_width=True):
        st.session_state.rows.append(dict(element='Nd',ppm=100.0,formula=SALTS['Nd'][0],purity=100.0))
        st.rerun()
with c2:
    st.write('Select a salt or enter a custom formula; use `·` or `.` for waters of hydration.')

results=[]
remove=None
for i,row in enumerate(st.session_state.rows):
    with st.container(border=True):
        a,b,c,d,e = st.columns([1.15,1.1,2.5,1.1,0.55])
        elements = sorted(ATOMIC)
        with a:
            element = st.selectbox('Element',elements,index=elements.index(row['element']),key=f'el_{i}')
        with b:
            ppm = st.number_input('Target ppm',min_value=0.0,value=float(row['ppm']),step=10.0,key=f'ppm_{i}')
        with c:
            options = SALTS.get(element,[])
            options = options + ['Custom formula']
            previous = row['formula']
            initial = previous if previous in options else (options[0] if row['element'] != element and len(options)>1 else 'Custom formula')
            selected = st.selectbox('Salt',options,index=options.index(initial),key=f'salt_{i}')
            formula = st.text_input('Custom chemical formula',value=previous if selected=='Custom formula' and row['element']==element else '',key=f'custom_{i}') if selected=='Custom formula' else selected
        with d:
            purity = st.number_input('Purity (%)',min_value=0.01,max_value=100.0,value=float(row['purity']),step=0.5,key=f'purity_{i}')
        with e:
            st.write('Remove')
            if st.button('✕',key=f'remove_{i}'): remove=i
        row.update(element=element,ppm=ppm,formula=formula,purity=purity)
        try:
            mw,metal,salt=calculate(element,ppm,volume,formula,purity)
            results.append({'Element':element,'Target (ppm)':ppm,'Salt formula':formula,'Purity (%)':purity,'Molar mass (g/mol)':round(mw,4),'Element needed (mg)':round(metal,4),'Salt to weigh (mg)':round(salt,4),'Salt to weigh (g)':round(salt/1000,6)})
            st.success(f'Weigh **{salt:,.3f} mg** ({salt/1000:,.6f} g) of {formula}.')
        except ValueError as exc:
            st.error(str(exc))
if remove is not None:
    st.session_state.rows.pop(remove)
    st.rerun()

st.subheader('Preparation summary')
if results:
    df=pd.DataFrame(results)
    st.dataframe(df,hide_index=True,use_container_width=True)
    st.download_button('⬇️ Download preparation sheet (CSV)',df.to_csv(index=False).encode('utf-8-sig'),'solution_preparation.csv','text/csv')
st.info('Dissolve each weighed salt in less than the final volume of solvent, combine if chemically compatible, and bring to the specified FINAL volume in a volumetric flask. Check precipitation, oxidation state, and stability before mixing. Verify hydrate form and assay on the reagent label. This tool assumes each selected salt is the only source of its target element and does not model solution chemistry.')
