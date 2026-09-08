"""Pruebas geométricas y de separación de ramas. Ejecutar: python test_animaciones.py"""
import importlib.util
from pathlib import Path
import sys
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parent

def cargar(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, ROOT / archivo)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = modulo
    spec.loader.exec_module(modulo)
    return modulo

arcos = cargar('arcos', '01_arcos_sin_rayos.py')
espirales = cargar('espirales', '02_estrella_logaritmica.py')

class Pruebas(unittest.TestCase):
    def test_arcos_misma_parametrizacion(self):
        for c, rama in zip(arcos.C_VALORES, arcos.crear_ramas()):
            a,b=2*np.arctan(np.array([arcos.X_MIN,arcos.X_MAX])/abs(c))
            for u in np.linspace(0,1,99):
                x=abs(c)*np.tan((a+(b-a)*u)/2)
                self.assertLess(abs(rama.punto(u)-1/(x-1j*c)),1e-12)

    def test_arcos_son_semicircunferencias_derechas(self):
        self.assertEqual(len(arcos.crear_ramas()),5)
        for c,rama in zip(arcos.C_VALORES, arcos.crear_ramas()):
            self.assertTrue(np.all(rama.muestras.real>0))
            np.testing.assert_allclose(abs(rama.muestras-1j/(2*c)),1/(2*abs(c)),atol=1e-12)

    def test_espirales_geometria_original(self):
        betas=np.linspace(0,2*np.pi,espirales.N,endpoint=False)
        ramas=espirales.crear_ramas()
        self.assertEqual(len(ramas),24)
        for beta,rama in zip(betas,ramas):
            r=abs(rama.muestras)
            esperado=r*np.exp(1j*(beta+espirales.DELTA*np.log(r)))
            np.testing.assert_allclose(rama.muestras,esperado,atol=1e-12)
            self.assertAlmostEqual(r.min(),.03)
            self.assertAlmostEqual(r.max(),3.)
            for u in np.linspace(0,1,21):
                radial=3.+(.03-3.)*u
                self.assertLess(abs(rama.punto(u)-radial*np.exp(1j*(beta+.6*np.log(radial)))),1e-12)

    def test_radio_siempre_positivo(self):
        for m in [arcos,espirales]:
            eps=np.array([m.radio(s) for s in np.linspace(0,1,1001)])
            self.assertGreaterEqual(eps.min(),.1-1e-12)
            self.assertLessEqual(eps.max(),.4+1e-12)

    def test_resaltado_sin_uniones(self):
        segmentos=[np.array([-1+0j,0+0j,1+0j]),np.array([0+1j,0+2j])]
        z=arcos.unir_con_cortes(segmentos)
        self.assertTrue(np.isnan(z[3]))
        h=arcos.dentro_del_disco(z,0j,1.01)
        self.assertTrue(np.isnan(h[3]))
        self.assertTrue(np.isnan(h[-2]))
        self.assertTrue(np.all(abs(h[np.isfinite(h)])<1.01))

    def test_resaltado_incluye_otras_ramas(self):
        ramas=arcos.crear_ramas()
        centro=ramas[0].punto(.85)
        hits=sum(np.any(abs(r.muestras-centro)<.3) for r in ramas)
        self.assertGreater(hits,1)
        z=arcos.unir_con_cortes([r.muestras for r in ramas])
        h=arcos.dentro_del_disco(z,centro,.3)
        self.assertGreater(np.isfinite(h).sum(),0)
        self.assertTrue(np.all(abs(h[np.isfinite(h)]-centro)<.3))

    def test_recorrido_todas_las_ramas_y_fundido(self):
        for m in [arcos,espirales]:
            ramas=m.crear_ramas();rec=list(range(len(ramas)));cuadros=int(m.FPS*m.DURACION)
            observadas=set()
            for k in range(cuadros):
                j,u,alpha=m.estado(k,cuadros,rec)
                observadas.add(j)
                self.assertTrue(0<=u<=1 and 0<=alpha<=1)
                self.assertTrue(np.isfinite(ramas[j].punto(u)))
            self.assertEqual(observadas,set(rec))

    def test_disco_no_se_recorta(self):
        for m in [arcos,espirales]:
            ramas=m.crear_ramas();rec=list(range(len(ramas)));cuadros=int(m.FPS*m.DURACION)
            fig,ax,act,_=m.preparar_figura(ramas,True,cuadros,rec)
            xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim()
            for k in range(0,cuadros,7):
                t,eps=act(k)
                self.assertTrue(xmin<t.real-eps<t.real+eps<xmax)
                self.assertTrue(ymin<t.imag-eps<t.imag+eps<ymax)
            m.plt.close(fig)

    def test_validacion_basica(self):
        for m in [arcos,espirales]:
            ramas=m.crear_ramas()
            with self.assertRaises(ValueError):m.validar(ramas,[999],20,25,130)
            with self.assertRaises(ValueError):m.validar(ramas,[0],-1,25,130)

if __name__=='__main__':
    unittest.main(verbosity=2)
