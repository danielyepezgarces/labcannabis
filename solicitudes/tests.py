from django.test import TestCase
from django.contrib.auth.models import User, Group
from datetime import date, timedelta
from .models import Solicitud, Muestra, TipoAnalisis, RecepcionMuestra


class SolicitudModelTest(TestCase):
    """Tests for Solicitud model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_solicitud_creation(self):
        """Test creating a solicitud"""
        solicitud = Solicitud.objects.create(
            solicitante_nombre='Juan Pérez',
            solicitante_area='AGRONOMIA',
            solicitante_cargo='Ingeniero Agrónomo',
            solicitante_email='juan@example.com',
            creado_por=self.user
        )
        
        self.assertIsNotNone(solicitud.codigo)
        self.assertTrue(solicitud.codigo.startswith('QC'))
        self.assertEqual(solicitud.estado, 'RADICADA')
    
    def test_codigo_autogeneration(self):
        """Test automatic code generation"""
        solicitud1 = Solicitud.objects.create(
            solicitante_nombre='Test 1',
            solicitante_area='PRODUCCION',
            solicitante_cargo='Test',
            solicitante_email='test1@example.com',
            creado_por=self.user
        )
        
        solicitud2 = Solicitud.objects.create(
            solicitante_nombre='Test 2',
            solicitante_area='PRODUCCION',
            solicitante_cargo='Test',
            solicitante_email='test2@example.com',
            creado_por=self.user
        )
        
        # Extract numbers from codes
        num1 = int(solicitud1.codigo[2:6])
        num2 = int(solicitud2.codigo[2:6])
        
        self.assertEqual(num2, num1 + 1)
    
    def test_state_transitions(self):
        """Test state machine transitions"""
        solicitud = Solicitud.objects.create(
            solicitante_nombre='Test',
            solicitante_area='PRODUCCION',
            solicitante_cargo='Test',
            solicitante_email='test@example.com',
            creado_por=self.user
        )
        
        # Test transition to PENDIENTE_RECEPCION
        solicitud.enviar_a_recepcion()
        solicitud.save()
        self.assertEqual(solicitud.estado, 'PENDIENTE_RECEPCION')
        
        # Test transition to RECIBIDA
        solicitud.recibir_conforme()
        solicitud.save()
        self.assertEqual(solicitud.estado, 'RECIBIDA')
        
        # Test transition to EN_ANALISIS
        solicitud.iniciar_analisis()
        solicitud.save()
        self.assertEqual(solicitud.estado, 'EN_ANALISIS')
        
        # Test transition to COMPLETADA
        solicitud.completar_analisis()
        solicitud.save()
        self.assertEqual(solicitud.estado, 'COMPLETADA')


class MuestraModelTest(TestCase):
    """Tests for Muestra model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.solicitud = Solicitud.objects.create(
            solicitante_nombre='Test',
            solicitante_area='PRODUCCION',
            solicitante_cargo='Test',
            solicitante_email='test@example.com',
            creado_por=self.user
        )
        
        self.tipo_analisis = TipoAnalisis.objects.create(
            nombre='Test Análisis',
            categoria='FISICO',
            descripcion='Test'
        )
    
    def test_muestra_creation(self):
        """Test creating a muestra"""
        muestra = Muestra.objects.create(
            solicitud=self.solicitud,
            nombre_producto='Producto Test',
            numero_lote='LOT001',
            fecha_fabricacion=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=365),
            numero_muestras_enviadas=5,
            cantidad_por_muestra='100g',
            tipo_muestra='FLOR',
            condiciones_almacenamiento='AMBIENTE',
            fecha_entrega_laboratorio=date.today(),
            tipo_analisis='EN_PROCESO',
            prioridad='NORMAL'
        )
        
        self.assertEqual(muestra.solicitud, self.solicitud)
        self.assertEqual(muestra.nombre_producto, 'Producto Test')
    
    def test_muestra_analisis_relationship(self):
        """Test ManyToMany relationship with TipoAnalisis"""
        muestra = Muestra.objects.create(
            solicitud=self.solicitud,
            nombre_producto='Producto Test',
            numero_lote='LOT001',
            fecha_fabricacion=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=365),
            numero_muestras_enviadas=5,
            cantidad_por_muestra='100g',
            tipo_muestra='FLOR',
            condiciones_almacenamiento='AMBIENTE',
            fecha_entrega_laboratorio=date.today(),
            tipo_analisis='EN_PROCESO',
            prioridad='NORMAL'
        )
        
        muestra.analisis_solicitados.add(self.tipo_analisis)
        
        self.assertEqual(muestra.analisis_solicitados.count(), 1)
        self.assertIn(self.tipo_analisis, muestra.analisis_solicitados.all())


class RecepcionMuestraTest(TestCase):
    """Tests for RecepcionMuestra model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.solicitud = Solicitud.objects.create(
            solicitante_nombre='Test',
            solicitante_area='PRODUCCION',
            solicitante_cargo='Test',
            solicitante_email='test@example.com',
            creado_por=self.user
        )
        # Move to PENDIENTE_RECEPCION state
        self.solicitud.enviar_a_recepcion()
        self.solicitud.save()
    
    def test_recepcion_conforme(self):
        """Test conforme reception"""
        recepcion = RecepcionMuestra.objects.create(
            solicitud=self.solicitud,
            recibido_por=self.user,
            condicion='CONFORME',
            observaciones='Todo en orden'
        )
        
        # Get fresh instance from database
        solicitud = Solicitud.objects.get(pk=self.solicitud.pk)
        
        self.assertEqual(solicitud.estado, 'RECIBIDA')
    
    def test_recepcion_no_conforme(self):
        """Test non-conforme reception"""
        recepcion = RecepcionMuestra.objects.create(
            solicitud=self.solicitud,
            recibido_por=self.user,
            condicion='NO_CONFORME',
            observaciones='Muestras dañadas'
        )
        
        # Get fresh instance from database
        solicitud = Solicitud.objects.get(pk=self.solicitud.pk)
        
        self.assertEqual(solicitud.estado, 'RECHAZADA')


class TipoAnalisisTest(TestCase):
    """Tests for TipoAnalisis model"""
    
    def test_tipo_analisis_creation(self):
        """Test creating analysis types"""
        tipo = TipoAnalisis.objects.create(
            nombre='Humedad',
            categoria='FISICO',
            descripcion='Análisis de humedad'
        )
        
        self.assertEqual(tipo.nombre, 'Humedad')
        self.assertEqual(tipo.categoria, 'FISICO')
        self.assertEqual(str(tipo), 'Físicos - Humedad')


class AdminEstadoModificationTest(TestCase):
    """Tests for admin estado modification functionality"""
    
    def setUp(self):
        # Create groups
        self.admin_group = Group.objects.create(name='Administrador')
        self.solicitante_group = Group.objects.create(name='Solicitante')
        
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        self.admin_user.groups.add(self.admin_group)
        
        self.solicitante_user = User.objects.create_user(
            username='solicitante',
            email='solicitante@test.com',
            password='solpass123'
        )
        self.solicitante_user.groups.add(self.solicitante_group)
        
        # Create test solicitud
        self.solicitud = Solicitud.objects.create(
            solicitante_nombre='Test',
            solicitante_area='PRODUCCION',
            solicitante_cargo='Test',
            solicitante_email='test@example.com',
            creado_por=self.admin_user
        )
    
    def test_admin_can_set_estado_directly(self):
        """Test that admin can set estado directly using set_estado_admin method"""
        self.assertEqual(self.solicitud.estado, 'RADICADA')
        
        # Admin should be able to change estado directly
        self.solicitud.set_estado_admin('COMPLETADA')
        self.solicitud.save()
        
        # Reload from database
        solicitud = Solicitud.objects.get(pk=self.solicitud.pk)
        self.assertEqual(solicitud.estado, 'COMPLETADA')
    
    def test_set_estado_admin_method_exists(self):
        """Test that set_estado_admin method exists and is callable"""
        self.assertTrue(hasattr(self.solicitud, 'set_estado_admin'))
        self.assertTrue(callable(getattr(self.solicitud, 'set_estado_admin')))
    
    def test_admin_bypass_fsm_protection(self):
        """Test that admin can bypass FSM state transitions"""
        # Normal FSM transition path would be:
        # RADICADA -> PENDIENTE_RECEPCION -> RECIBIDA -> EN_ANALISIS -> COMPLETADA
        
        # But admin should be able to jump directly from RADICADA to EN_ANALISIS
        self.assertEqual(self.solicitud.estado, 'RADICADA')
        
        self.solicitud.set_estado_admin('EN_ANALISIS')
        self.solicitud.save()
        
        solicitud = Solicitud.objects.get(pk=self.solicitud.pk)
        self.assertEqual(solicitud.estado, 'EN_ANALISIS')
    
    def test_normal_fsm_transitions_still_work(self):
        """Test that normal FSM transitions still work as expected"""
        self.assertEqual(self.solicitud.estado, 'RADICADA')
        
        # Test normal FSM transition
        self.solicitud.enviar_a_recepcion()
        self.solicitud.save()
        
        solicitud = Solicitud.objects.get(pk=self.solicitud.pk)
        self.assertEqual(solicitud.estado, 'PENDIENTE_RECEPCION')
    
    def test_set_estado_admin_validates_input(self):
        """Test that set_estado_admin validates the estado value"""
        with self.assertRaises(ValueError) as context:
            self.solicitud.set_estado_admin('INVALID_ESTADO')
        
        self.assertIn('Invalid estado', str(context.exception))
    
    def test_set_estado_admin_accepts_valid_values(self):
        """Test that set_estado_admin accepts all valid estado values"""
        valid_estados = ['RADICADA', 'PENDIENTE_RECEPCION', 'RECIBIDA', 
                        'EN_ANALISIS', 'COMPLETADA', 'RECHAZADA']
        
        for estado in valid_estados:
            solicitud = Solicitud.objects.create(
                solicitante_nombre='Test',
                solicitante_area='PRODUCCION',
                solicitante_cargo='Test',
                solicitante_email='test@example.com',
                creado_por=self.admin_user
            )
            
            # Should not raise any exception
            solicitud.set_estado_admin(estado)
            solicitud.save()
            
            # Verify it was saved correctly
            solicitud = Solicitud.objects.get(pk=solicitud.pk)
            self.assertEqual(solicitud.estado, estado)
            
            # Clean up
            solicitud.delete()

