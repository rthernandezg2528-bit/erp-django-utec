"""Suite de pruebas W06 — Validators, integridad y comportamiento de modelos.

Ejecutar con:
    python manage.py test tests.test_w06_validadores --verbosity=2
"""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from clientes.models       import Cliente
from configuracion.models  import ConfiguracionERP
from productos.models      import Categoria, Producto
from proveedores.models    import Proveedor
from ventas.models         import DetalleVenta, Pedido, Venta


def crear_fixtures():
    """Crea objetos base para los tests."""
    cat  = Categoria.objects.create(nombre='Test Cat')
    prov = Proveedor.objects.create(nombre='Prov Test', correo='prov@t.com')
    cli  = Cliente.objects.create(nombre='Cliente Test', correo='cli@t.com')
    prod = Producto.objects.create(
        nombre='Prod Test', precio=Decimal('100.00'), stock=10, categoria=cat
    )
    return cat, prov, cli, prod


# ── BLOQUE 1: Validators de campos ───────────────────────────────────────

class ValidadoresCamposTest(TestCase):

    def setUp(self):
        self.cat = Categoria.objects.create(nombre='Electrónica')

    def test_precio_negativo_lanza_validation_error(self):
        prod = Producto(nombre='X', precio=Decimal('-1.00'),
                        stock=5, categoria=self.cat)
        with self.assertRaises(ValidationError) as ctx:
            prod.full_clean()
        self.assertIn('precio', ctx.exception.message_dict)

    def test_precio_cero_es_valido(self):
        prod = Producto(nombre='Gratis', precio=Decimal('0.00'),
                        stock=5, categoria=self.cat)
        try:
            prod.full_clean()
        except ValidationError as e:
            if 'precio' in e.message_dict:
                self.fail("Precio 0.00 no debería lanzar ValidationError")

    def test_stock_negativo_lanza_validation_error(self):
        prod = Producto(nombre='Y', precio=Decimal('50.00'),
                        stock=-1, categoria=self.cat)
        with self.assertRaises(ValidationError) as ctx:
            prod.full_clean()
        self.assertIn('stock', ctx.exception.message_dict)

    def test_detalle_cantidad_cero_lanza_error(self):
        cli  = Cliente.objects.create(nombre='C', correo='c@t.com')
        prod = Producto.objects.create(
            nombre='P', precio=Decimal('10.00'), stock=5, categoria=self.cat
        )
        venta = Venta.objects.create(cliente=cli)
        det = DetalleVenta(venta=venta, producto=prod,
                           cantidad=0, precio_unitario=Decimal('10.00'))
        with self.assertRaises(ValidationError) as ctx:
            det.full_clean()
        self.assertIn('cantidad', ctx.exception.message_dict)


# ── BLOQUE 2: Unicidad ───────────────────────────────────────────────────

class UnicidadTest(TestCase):

    def test_correo_duplicado_cliente_lanza_integrity_error(self):
        Cliente.objects.create(nombre='A', correo='dup@test.com')
        with self.assertRaises(IntegrityError):
            Cliente.objects.create(nombre='B', correo='dup@test.com')

    def test_correo_duplicado_proveedor_lanza_integrity_error(self):
        Proveedor.objects.create(nombre='P1', correo='dup@prov.com')
        with self.assertRaises(IntegrityError):
            Proveedor.objects.create(nombre='P2', correo='dup@prov.com')


# ── BLOQUE 3: on_delete ──────────────────────────────────────────────────

class OnDeleteTest(TestCase):

    def setUp(self):
        self.cat, self.prov, self.cli, self.prod = crear_fixtures()

    def test_categoria_protect_no_borrar_con_productos(self):
        with self.assertRaises(ProtectedError):
            self.cat.delete()

    def test_proveedor_set_null_al_borrar(self):
        self.prod.proveedor = self.prov
        self.prod.save()
        self.prov.delete()
        self.prod.refresh_from_db()
        self.assertIsNone(self.prod.proveedor)

    def test_venta_protect_no_borrar_cliente_con_ventas(self):
        Venta.objects.create(cliente=self.cli)
        with self.assertRaises(ProtectedError):
            self.cli.delete()

    def test_detalle_venta_cascade_al_borrar_venta(self):
        venta = Venta.objects.create(cliente=self.cli)
        DetalleVenta.objects.create(venta=venta, producto=self.prod,
                                    cantidad=2, precio_unitario=Decimal('100.00'))
        self.assertEqual(DetalleVenta.objects.count(), 1)
        venta.delete()
        self.assertEqual(DetalleVenta.objects.count(), 0)

    def test_producto_protect_no_borrar_con_detalles(self):
        venta = Venta.objects.create(cliente=self.cli)
        DetalleVenta.objects.create(venta=venta, producto=self.prod,
                                    cantidad=1, precio_unitario=Decimal('100.00'))
        with self.assertRaises(ProtectedError):
            self.prod.delete()


# ── BLOQUE 4: Precio histórico y total ───────────────────────────────────

class PrecioHistoricoTest(TestCase):

    def setUp(self):
        cat = Categoria.objects.create(nombre='Cat')
        self.prod = Producto.objects.create(
            nombre='P', precio=Decimal('200.00'), stock=5, categoria=cat
        )
        cli = Cliente.objects.create(nombre='C', correo='c@t.com')
        self.venta = Venta.objects.create(cliente=cli)

    def test_detalle_captura_precio_del_producto(self):
        det = DetalleVenta.objects.create(
            venta=self.venta, producto=self.prod,
            cantidad=1, precio_unitario=None
        )
        self.assertEqual(det.precio_unitario, Decimal('200.00'))

    def test_detalle_no_sobreescribe_precio_cero(self):
        det = DetalleVenta.objects.create(
            venta=self.venta, producto=self.prod,
            cantidad=1, precio_unitario=Decimal('0.00')
        )
        self.assertEqual(det.precio_unitario, Decimal('0.00'))

    def test_venta_total_dos_lineas(self):
        cat2  = Categoria.objects.create(nombre='Cat2')
        prod2 = Producto.objects.create(
            nombre='P2', precio=Decimal('50.00'), stock=5, categoria=cat2
        )
        DetalleVenta.objects.create(venta=self.venta, producto=self.prod,
                                    cantidad=3, precio_unitario=Decimal('200.00'))
        DetalleVenta.objects.create(venta=self.venta, producto=prod2,
                                    cantidad=2, precio_unitario=Decimal('50.00'))
        self.assertEqual(self.venta.total, Decimal('700.00'))


# ── BLOQUE 5: __str__ y singleton ────────────────────────────────────────

class StrYSingletonTest(TestCase):

    def test_venta_str_contiene_pk_y_cliente(self):
        cli   = Cliente.objects.create(nombre='María', correo='m@t.com')
        venta = Venta.objects.create(cliente=cli)
        resultado = str(venta)
        self.assertIn(str(venta.pk), resultado)
        self.assertIn('María', resultado)

    def test_pedido_choices_pendiente_por_defecto(self):
        cli = Cliente.objects.create(nombre='Z', correo='z@t.com')
        p   = Pedido.objects.create(numero_pedido='PED-001', cliente=cli)
        self.assertEqual(p.estado, 'pendiente')

    def test_configuracion_singleton_pk_siempre_1(self):
        cfg = ConfiguracionERP.objects.create(pk=1, nombre_empresa='Empresa A')
        cfg.nombre_empresa = 'Empresa B'
        cfg.save()
        self.assertEqual(ConfiguracionERP.objects.count(), 1)
        self.assertEqual(ConfiguracionERP.objects.first().pk, 1)