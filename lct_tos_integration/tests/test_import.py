from openerp.tests.common import TransactionCase
from openerp.osv import osv
import os
from ftplib import FTP
from lxml import etree as ET
from StringIO import StringIO
import import_export_tools as iet


class TestImport(TransactionCase):

    def setUp(self):
        super(TestImport, self).setUp()
        self.ftp_config_model = self.registry('ftp.config')
        self.invoice_model = self.registry('account.invoice')
        self.partner_model = self.registry('res.partner')
        self.import_data_model = self.registry('lct.tos.import.data')
        self.vsl_model = self.registry('lct.tos.vessel')
        cr, uid = self.cr, self.uid
        config_ids = self.ftp_config_model.search(cr, uid, [])
        self.config = config = config_ids and self.ftp_config_model.browse(cr, uid, config_ids)[0] or False
        currency_id = self.registry('res.currency').search(cr, uid, [('name','=','XOF')])[0]
        self.registry('res.company').write(cr, uid, 1, {'currency_id': currency_id})
        self.registry('product.price.type').write(cr, uid, 1, {'currency_id': currency_id})
        self.registry('product.price.type').write(cr, uid, 2, {'currency_id': currency_id})

    def test_only_one_active_config(self):
        cr, uid = self.cr, self.uid
        if not self.config:
            return True
        config2 = dict(
            name="Config2",
            active=True,
            addr='Address',
            user='user',
            psswd='password',
            inbound_path='in_path',
            outbound_path='out_path'
            )
        with self.assertRaises(Exception,
                msg='Creating a second active config should raise an error'):
            self.ftp_config_model.create(cr, uid, config2)

    def _create_pricelist(self):
        cr, uid = self.cr, self.uid
        pricelist_model = self.registry('product.pricelist')
        product_model = self.registry('product.product')
        imd_model = self.registry('ir.model.data')

        product_id = imd_model.get_record_id(cr, uid, 'lct_tos_integration', 'export_storage_20_full_gp')
        product_model.write(cr, uid, [product_id], {'list_price': 50.})
        tariff_rate_vals = [
            (0,0,{
                'product_id': product_id,
                'min_quantity': 0,
                'sequence': 1,
                'slab_rate': True,
                'price_discount_rate1': -0.5,
                'price_discount_rate2': -0.25,
                'price_discount_rate3': 0.,
                'free_period': 5,
                'first_slab_last_day': 10,
                'second_slab_last_day': 15,
                'base': 1,
            }),
        ]
        product_id = imd_model.get_record_id(cr, uid, 'lct_tos_integration', 'export_reeferelectricity_20')
        product_model.write(cr, uid, [product_id], {'list_price': 16.})
        tariff_rate_vals.append(
            (0,0,{
                'product_id': product_id,
                'min_quantity': 0,
                'sequence': 1,
                'slab_rate': True,
                'price_discount_rate1': -0.4,
                'price_discount_rate2': -0.3,
                'price_discount_rate3': 0.,
                'free_period': 5,
                'first_slab_last_day': 10,
                'second_slab_last_day': 15,
                'base': 1,
            })
        )
        product_id = imd_model.get_record_id(cr, uid, 'lct_tos_integration', 'import_reeferelectricity_40')
        product_model.write(cr, uid, [product_id], {'list_price': 58.})
        tariff_rate_vals.append(
            (0,0,{
                'product_id': product_id,
                'min_quantity': 0,
                'sequence': 1,
                'slab_rate': True,
                'price_discount_rate1': -0.6,
                'price_discount_rate2': -0.2,
                'price_discount_rate3': 0.,
                'free_period': 5,
                'first_slab_last_day': 10,
                'second_slab_last_day': 15,
                'base': 1,
            })
        )
        product_id = imd_model.get_record_id(cr, uid, 'lct_tos_integration', 'import_discharge_20_full_gp')
        product_model.write(cr, uid, [product_id], {'list_price': 15.})
        tariff_rate_vals.append(
            (0,0,{
                'product_id': product_id,
                'min_quantity': 0,
                'sequence': 1,
                'slab_rate': False,
                'price_discount': -0.25,
                'base': 1,
            })
        )
        product_id = imd_model.get_record_id(cr, uid, 'lct_tos_integration', 'import_discharge_40_full_gp')
        product_model.write(cr, uid, [product_id], {'list_price': 20.})
        tariff_rate_vals.append(
            (0,0,{
                'product_id': product_id,
                'min_quantity': 0,
                'sequence': 1,
                'slab_rate': False,
                'price_discount': -0.5,
                'base': 1,
            })
        )
        product_id = imd_model.get_record_id(cr, uid, 'lct_tos_integration', 'gearboxcount')
        product_model.write(cr, uid, [product_id], {'list_price': 11.})
        tariff_rate_vals.append(
            (0,0,{
                'product_id': product_id,
                'min_quantity': 0,
                'sequence': 1,
                'slab_rate': False,
                'price_discount': -0.3,
                'base': 1,
            })
        )
        product_id = imd_model.get_record_id(cr, uid, 'lct_tos_integration', 'hatchcovermoves')
        product_model.write(cr, uid, [product_id], {'list_price': 13.})
        tariff_rate_vals.append(
            (0,0,{
                'product_id': product_id,
                'min_quantity': 0,
                'sequence': 1,
                'slab_rate': False,
                'price_discount': -0.4,
                'base': 1,
            })
        )
        product_id = imd_model.get_record_id(cr, uid, 'lct_tos_integration', 'dockage_loa160mandbelow')
        product_model.write(cr, uid, [product_id], {'list_price': 13.})
        tariff_rate_vals.append(
            (0,0,{
                'product_id': product_id,
                'min_quantity': 0,
                'sequence': 1,
                'slab_rate': False,
                'price_discount': -0.0,
                'base': 1,
            })
        )
        product_id = imd_model.get_record_id(cr, uid, 'lct_tos_integration', 'dockage_loa160mto360m')
        product_model.write(cr, uid, [product_id], {'list_price': 13.})
        tariff_rate_vals.append(
            (0,0,{
                'product_id': product_id,
                'min_quantity': 0,
                'sequence': 1,
                'slab_rate': False,
                'price_discount': -0.0,
                'base': 1,
            })
        )
        product_id = imd_model.get_record_id(cr, uid, 'lct_tos_integration', 'dockage_loa360mandabove')
        product_model.write(cr, uid, [product_id], {'list_price': 13.})
        tariff_rate_vals.append(
            (0,0,{
                'product_id': product_id,
                'min_quantity': 0,
                'sequence': 1,
                'slab_rate': False,
                'price_discount': -0.0,
                'base': 1,
            })
        )
        tariff_vals = [
            (0,0,{
                'name': 'Test Tariff',
                'items_id': tariff_rate_vals,
            }),
        ]
        tariff_template_vals = {
            'name': 'Test Tariff Template',
            'currency_id': 42,
            'type': 'sale',
            'version_id': tariff_vals,
        }
        pricelist_model.create(cr, uid, tariff_template_vals)
        self.pricelist = pricelist_model.browse(cr, uid, pricelist_model.create(cr, uid, tariff_template_vals))

    def _prepare_import(self):
        cr, uid = self.cr, self.uid
        config = self.config
        self._create_pricelist()
        self.partner_id = self.partner_model.search(cr, uid, [('name', '=', 'MSK')])
        if self.partner_id:
            self.partner_id = self.partner_id[0]
            self.partner_model.write(cr, uid, [self.partner_id], {'property_product_pricelist': self.pricelist.id})
        else:
            self.partner_id = self.partner_model.create(cr, uid,{
                'name': 'Test Customer',
                'property_product_pricelist': self.pricelist.id,
                })

        ftp = FTP(host=config['addr'], user=config['user'], passwd=config['psswd'])
        ftp.cwd(config['outbound_path'])
        iet.purge_ftp(ftp, omit=['done'])

        xml_files = []
        local_path_path = os.path.join(__file__.split(__file__.split(os.sep)[-1])[0], 'xml_files')

        app_dir = os.path.join(local_path_path, 'APP_XML_files')
        app_files = [os.path.join(app_dir, file_name) for file_name in  os.listdir(app_dir)]
        for xml_file in app_files:
            f = iet.set_appointment_customer(open(xml_file), self.partner_id)
            file_name = xml_file.split(os.sep)[-1]
            xml_files.append((file_name, f))

        vbl_dir = os.path.join(local_path_path, 'VBL_XML_files')
        vbl_files = [os.path.join(vbl_dir, file_name) for file_name in  os.listdir(vbl_dir)]
        for xml_file in vbl_files:
            f = iet.set_vbilling_customer(open(xml_file), self.partner_id)
            file_name = xml_file.split(os.sep)[-1]
            xml_files.append((file_name, f))

        ves_dir = os.path.join(local_path_path, 'VES_XML_files')
        ves_files = [os.path.join(ves_dir, file_name) for file_name in  os.listdir(ves_dir)]
        for xml_file in ves_files:
            f = open(xml_file)
            file_name = xml_file.split(os.sep)[-1]
            xml_files.append((file_name, f))

        vcl_dir = os.path.join(local_path_path, 'VCL_XML_files')
        vcl_files = [os.path.join(vcl_dir, file_name) for file_name in  os.listdir(vcl_dir)]
        for xml_file in vcl_files:
            f = iet.set_dockage_customer(open(xml_file), self.partner_id)
            file_name = xml_file.split(os.sep)[-1]
            xml_files.append((file_name, f))

        for xml_file in xml_files:
            self.assertTrue(iet.upload_file(ftp, xml_file[1], xml_file[0]))

    def test_import(self):
        cr, uid = self.cr, self.uid
        if not self.config:
            return True
        ftp_config_model = self.ftp_config_model
        invoice_model, import_data_model = self.invoice_model, self.import_data_model
        product_model = self.registry('product.product')
        self._prepare_import()
        vsl_ids = self.vsl_model.search(cr, uid, [])
        self.vsl_model.unlink(cr, uid, vsl_ids)

        vessel_ids = self.invoice_model.search(cr, uid, [('type2','=','vessel')])
        appoint_ids = self.invoice_model.search(cr, uid, [('type2','=','appointment')])
        ftp_config_model.button_import_ftp_data(cr, uid, [self.config.id])

        appoints = invoice_model.browse(cr, uid, invoice_model.search(cr, uid, [('type2','=','appointment'), ('id', 'not in', appoint_ids)], order='appoint_ref'))
        self.assertEqual(len(appoints), 2, 'Importing should create 2 appointments')
        self.assertTrue(appoints[0].appoint_ref == 'LCT2014062400289', 'Importing should create an appointment with reference: LCT2014062400289')
        self.assertTrue(appoints[1].appoint_ref == 'LCT2014070900019', 'Importing should create an appointment with reference: LCT2014070900019')
        # TODO : Write tests for appointments

        vessels = invoice_model.browse(cr, uid, invoice_model.search(cr, uid, [('type2','=','vessel'), ('id', 'not in', vessel_ids)], order='call_sign'))
        self.assertTrue(len(vessels) == 1, 'Importing should create 1 vessel billing')

        lines = sorted(vessels[0].invoice_line, key=lambda x: x.name.lower())
        self.assertEqual(len(lines), 4)

        self.assertTrue(lines[0].name == 'Gearbox count')
        self.assertTrue(lines[0].quantity == 14)
        self.assertTrue(lines[0].price_unit == 7.7)
        self.assertTrue(lines[1].name == 'Hatchcover moves')
        self.assertTrue(lines[1].quantity == 6)
        self.assertTrue(lines[1].price_unit == 7.8)
        self.assertTrue(lines[2].name == 'Import Discharge 20 Full GP')
        self.assertTrue(lines[2].quantity == 1)
        self.assertTrue(lines[2].price_unit == 11.25)
        self.assertTrue(lines[3].name == 'Import Discharge 40 Full GP')
        self.assertTrue(lines[3].quantity == 1)
        self.assertTrue(lines[3].price_unit == 10.)

        vesselsafter = len(self.vsl_model.search(cr, uid, []))
        self.assertEqual(5, vesselsafter, 'Importing should create 5 Vessels')

    def test_02_vessel_dockage(self):
        cr, uid = self.cr, self.uid
        if not self.config:
            return True
        ftp_config_model = self.ftp_config_model
        invoice_model, import_data_model = self.invoice_model, self.import_data_model
        product_model = self.registry('product.product')

        self._prepare_import()
        dockage_ids = self.invoice_model.search(cr, uid, [('type2','=','dockage')])
        ftp_config_model.button_import_ftp_data(cr, uid, [self.config.id])

        dockages = invoice_model.browse(cr, uid, invoice_model.search(cr, uid, [('type2','=','dockage'), ('id', 'not in', dockage_ids)], order='appoint_ref'))
        self.assertEquals(len(dockages), 2)
        for dockage in dockages:
            self.assertEquals(len(dockage.invoice_line), 1)
            for line in dockage.invoice_line:
                self.assertEquals(line.quantity, 1)
                self.assertEquals(line.price_unit, 13.0)
