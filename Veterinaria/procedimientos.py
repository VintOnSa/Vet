from Apps.General.models import Procedimiento


procedimientos = [
    # Abdominocentesis
    Procedimiento(nombre="Abdominocentesis C", precio=26300),
    Procedimiento(nombre="Abdominocentesis C", precio=39000),
    Procedimiento(nombre="Abdominocentesis C", precio=52500),
    Procedimiento(nombre="Abdominocentesis F", precio=21000),
    Procedimiento(nombre="Abdominocentesis F", precio=26300),

    # Abscesos
    Procedimiento(nombre="Abscesos Canino A", precio=21000),
    Procedimiento(nombre="Abscesos Canino B", precio=35000),
    Procedimiento(nombre="Abscesos Canino C", precio=47300),
    Procedimiento(nombre="Abscesos Felino A", precio=15800),
    Procedimiento(nombre="Abscesos Felino B", precio=25000),
    Procedimiento(nombre="Abscesos Felino C", precio=31500),

    # Amputación
    Procedimiento(nombre="Amputación Canina", precio=63000),
    Procedimiento(nombre="Amputación Canina", precio=93000),
    Procedimiento(nombre="Amputación Canina", precio=123000),
    Procedimiento(nombre="Amputación Canina", precio=153000),
    Procedimiento(nombre="Amputación Canina", precio=183000),
    Procedimiento(nombre="Amputación Canina", precio=210000),

    Procedimiento(nombre="Amputación Felina A", precio=52500),
    Procedimiento(nombre="Amputación Felina B", precio=69000),
    Procedimiento(nombre="Amputación Felina C", precio=84000),

    # Antiparasitarios
    Procedimiento(nombre="Antiparasitaria Oral", precio=2100),
    Procedimiento(nombre="Antiparasitario Gatos", precio=2100),
    Procedimiento(nombre="Antiparasitario Oral", precio=3200),
    Procedimiento(nombre="Antiparasitario Gatos", precio=1100),
    Procedimiento(nombre="Antiparasitario Rg.", precio=4800),
    Procedimiento(nombre="Antiparasitario Rg.", precio=5800),

    # Aseo quirúrgico
    Procedimiento(nombre="Aseo Quirúrgico + S", precio=21000),
    Procedimiento(nombre="Aseo Quirúrgico + S", precio=42000),
    Procedimiento(nombre="Aseo Quirúrgico + S", precio=48000),
    Procedimiento(nombre="Aseo Quirúrgico + S", precio=63000),
    Procedimiento(nombre="Aseo Quirúrgico + S", precio=73500),

    Procedimiento(nombre="Aseo Quirúrgico Canino", precio=21000),
    Procedimiento(nombre="Aseo Quirúrgico Canino", precio=41000),
    Procedimiento(nombre="Aseo Quirúrgico Canino", precio=63000),

    Procedimiento(nombre="Aseo Quirúrgico Felino", precio=15800),
    Procedimiento(nombre="Aseo Quirúrgico Felino", precio=30000),
    Procedimiento(nombre="Aseo Quirúrgico Felino", precio=30000),
    Procedimiento(nombre="Aseo Quirúrgico Felino", precio=42000),

    # Castración
    Procedimiento(nombre="Castración Criptorquídica", precio=31500),
    Procedimiento(nombre="Castración Criptorquídica", precio=36800),
    Procedimiento(nombre="Castración Criptorquídica", precio=42000),
    Procedimiento(nombre="Castración Criptorquídica", precio=52000),
    Procedimiento(nombre="Castración Criptorquídica", precio=73500),

    Procedimiento(nombre="Castración Monorquídica", precio=21000),
    Procedimiento(nombre="Castración Monorquídica", precio=26300),
    Procedimiento(nombre="Castración Monorquídica", precio=31500),
    Procedimiento(nombre="Castración Monorquídica", precio=39000),
    Procedimiento(nombre="Castración Monorquídica", precio=52500),

    # Caudectomía
    Procedimiento(nombre="Caudectomía Terapéutica", precio=21000),
    Procedimiento(nombre="Caudectomía Terapéutica", precio=31500),
    Procedimiento(nombre="Caudectomía Terapéutica", precio=36800),
    Procedimiento(nombre="Caudectomía Terapéutica", precio=48000),
    Procedimiento(nombre="Caudectomía Terapéutica", precio=63000),

    # Certificados
    Procedimiento(nombre="Certificado De Salud", precio=7400),
    Procedimiento(nombre="Certificado De Salud", precio=10500),

    # Cesáreas
    Procedimiento(nombre="Cesárea Canina A", precio=52500),
    Procedimiento(nombre="Cesárea Canina B", precio=82500),
    Procedimiento(nombre="Cesárea Canina C", precio=100500),
    Procedimiento(nombre="Cesárea Canina D", precio=126000),

    Procedimiento(nombre="Cesárea Felina A", precio=36800),
    Procedimiento(nombre="Cesárea Felina B", precio=47300),

    Procedimiento(nombre="Cesárea Radical Canina", precio=36800),
    Procedimiento(nombre="Cesárea Radical Canina", precio=56800),
    Procedimiento(nombre="Cesárea Radical Canina", precio=73500),
    Procedimiento(nombre="Cesárea Radical Felina", precio=26300),
    Procedimiento(nombre="Cesárea Radical Felina", precio=36800),

    # Cherry Eye
    Procedimiento(nombre="Cherry Eye Bilateral", precio=47300),
    Procedimiento(nombre="Cherry Eye Bilateral", precio=63000),
    Procedimiento(nombre="Cherry Eye Bilateral", precio=63000),
    Procedimiento(nombre="Cherry Eye Bilateral", precio=82000),
    Procedimiento(nombre="Cherry Eye Bilateral", precio=105000),

    Procedimiento(nombre="Cherry Eye Unilateral", precio=31500),
    Procedimiento(nombre="Cherry Eye Unilateral", precio=42000),
    Procedimiento(nombre="Cherry Eye Unilateral", precio=47300),
    Procedimiento(nombre="Cherry Eye Unilateral", precio=62000),
    Procedimiento(nombre="Cherry Eye Unilateral", precio=84000),
    Procedimiento(nombre="Cherry Eye Unilateral", precio=84000),

    # Cistotomía
    Procedimiento(nombre="Cistotomía Canina A", precio=63000),
    Procedimiento(nombre="Cistotomía Canina B", precio=83000),
    Procedimiento(nombre="Cistotomía Canina C", precio=105000),

    Procedimiento(nombre="Cistotomía Felina A", precio=42000),
    Procedimiento(nombre="Cistotomía Felina B", precio=52000),
    Procedimiento(nombre="Cistotomía Felina C", precio=63000),

    # Consultas
    Procedimiento(nombre="Consulta AE. EX.", precio=15800),
    Procedimiento(nombre="Consulta AE. SJ.", precio=10500),
    Procedimiento(nombre="Consulta EX.", precio=9500),
    Procedimiento(nombre="Consulta SJ.", precio=6300),

    # Controles
    Procedimiento(nombre="Control EX.", precio=3700),
    Procedimiento(nombre="Control SJ.", precio=2700),

    # Corte de uñas
    Procedimiento(nombre="Corte De Uñas EX.", precio=5250),
    Procedimiento(nombre="Corte De Uñas SJ.", precio=3700),

    # Curaciones
    Procedimiento(nombre="Curaciones Caninas", precio=5300),
    Procedimiento(nombre="Curaciones Caninas", precio=18000),
    Procedimiento(nombre="Curaciones Caninas", precio=26300),
    Procedimiento(nombre="Curaciones Felinas", precio=5300),
    Procedimiento(nombre="Curaciones Felinas", precio=15800),

    # Destartraje
    Procedimiento(nombre="Destartraje Canino", precio=21000),
    Procedimiento(nombre="Destartraje Canino", precio=41000),
    Procedimiento(nombre="Destartraje Canino", precio=63000),
    Procedimiento(nombre="Destartraje Felino", precio=21000),
    Procedimiento(nombre="Destartraje Felino", precio=31500),

    # Entropión
    Procedimiento(nombre="Entropión Bilateral", precio=47300),
    Procedimiento(nombre="Entropión Bilateral", precio=57800),
    Procedimiento(nombre="Entropión Bilateral", precio=73500),
    Procedimiento(nombre="Entropión Bilateral", precio=100000),
    Procedimiento(nombre="Entropión Bilateral", precio=126000),

    Procedimiento(nombre="Entropión Unilateral", precio=31500),
    Procedimiento(nombre="Entropión Unilateral", precio=42000),
    Procedimiento(nombre="Entropión Unilateral", precio=42000),
    Procedimiento(nombre="Entropión Unilateral", precio=58000),
    Procedimiento(nombre="Entropión Unilateral", precio=73500),

    # Enucleación
    Procedimiento(nombre="Enucleación Unilateral", precio=26300),
    Procedimiento(nombre="Enucleación Unilateral", precio=31500),
    Procedimiento(nombre="Enucleación Unilateral", precio=36800),
    Procedimiento(nombre="Enucleación Unilateral", precio=48000),
    Procedimiento(nombre="Enucleación Unilateral", precio=63000),

    # Epuli
    Procedimiento(nombre="Epuli", precio=8400),

    # Esterilización
    Procedimiento(nombre="Esterilización Canina", precio=21000),
    Procedimiento(nombre="Esterilización Canina", precio=26300),
    Procedimiento(nombre="Esterilización Canina", precio=36800),
    Procedimiento(nombre="Esterilización Canina", precio=36800),
    Procedimiento(nombre="Esterilización Canina", precio=42000),
    Procedimiento(nombre="Esterilización Canina", precio=52500),
    Procedimiento(nombre="Esterilización Canina", precio=52500),
    Procedimiento(nombre="Esterilización Canina", precio=63000),
    Procedimiento(nombre="Esterilización Canina", precio=68300),
    Procedimiento(nombre="Esterilización Canina", precio=78800),

    Procedimiento(nombre="Esterilización Felina", precio=15800),
    Procedimiento(nombre="Esterilización Felina", precio=21000),

    # Eutanasia
    Procedimiento(nombre="Eutanasia Previa A E.", precio=21000),
    Procedimiento(nombre="Eutanasia Previa A E.", precio=26300),
    Procedimiento(nombre="Eutanasia Previa A E.", precio=31000),
    Procedimiento(nombre="Eutanasia Previa A E.", precio=42000),
    Procedimiento(nombre="Eutanasia Previa A E.", precio=42000),
    Procedimiento(nombre="Eutanasia Previa A E.", precio=63000),

    # Falangectomía
    Procedimiento(nombre="Falangectomía Canina", precio=21000),
    Procedimiento(nombre="Falangectomía Canina", precio=31000),
    Procedimiento(nombre="Falangectomía Canina", precio=42000),

    Procedimiento(nombre="Falangectomía Felina", precio=15800),
    Procedimiento(nombre="Falangectomía Felina", precio=22000),
    Procedimiento(nombre="Falangectomía Felina", precio=31500),

    # Flushing
    Procedimiento(nombre="Flushing Felino", precio=12000),

    # Hemometra
    Procedimiento(nombre="Hemometra Canina A", precio=31500),
    Procedimiento(nombre="Hemometra Canina B", precio=51500),
    Procedimiento(nombre="Hemometra Canina C", precio=71500),
    Procedimiento(nombre="Hemometra Canina D", precio=94500),
    Procedimiento(nombre="Hemometra Felina A", precio=21000),
    Procedimiento(nombre="Hemometra Felina B", precio=31500),

    # Hernias
    Procedimiento(nombre="Hernia Inguinal Canina", precio=31500),
    Procedimiento(nombre="Hernia Inguinal Canina", precio=48000),
    Procedimiento(nombre="Hernia Inguinal Canina", precio=68300),
    Procedimiento(nombre="Hernia Inguinal Felina", precio=21000),
    Procedimiento(nombre="Hernia Inguinal Felina", precio=47300),

    Procedimiento(nombre="Hernia Perianal Bilateral", precio=63000),
    Procedimiento(nombre="Hernia Perianal Bilateral", precio=84000),
    Procedimiento(nombre="Hernia Perianal Bilateral", precio=104000),
    Procedimiento(nombre="Hernia Perianal Bilateral", precio=126000),

    Procedimiento(nombre="Hernia Perianal Canina", precio=47300),
    Procedimiento(nombre="Hernia Perianal Canina", precio=57300),
    Procedimiento(nombre="Hernia Perianal Canina", precio=68300),

    Procedimiento(nombre="Hernia Perianal Felina", precio=42000),
    Procedimiento(nombre="Hernia Perianal Felina", precio=47300),

    Procedimiento(nombre="Hernia Umbilical Canina", precio=21000),
    Procedimiento(nombre="Hernia Umbilical Canina", precio=42500),
    Procedimiento(nombre="Hernia Umbilical Felina", precio=15800),
    Procedimiento(nombre="Hernia Umbilical Felina", precio=26300),

    # Implantación de microchip
    Procedimiento(nombre="Implantación De Microchip", precio=7400),
    Procedimiento(nombre="Implantación De Microchip", precio=10500),

    # Laparotomía
    Procedimiento(nombre="Laparotomía Canina", precio=26300),
    Procedimiento(nombre="Laparotomía Canina", precio=39000),
    Procedimiento(nombre="Laparotomía Canina", precio=52500),
    Procedimiento(nombre="Laparotomía Felina", precio=21000),
    Procedimiento(nombre="Laparotomía Felina", precio=31500),

    # Lavado de oído
    Procedimiento(nombre="Lavado De Oído Canino", precio=21000),
    Procedimiento(nombre="Lavado De Oído Canino", precio=31000),
    Procedimiento(nombre="Lavado De Oído Canino", precio=42000),
    Procedimiento(nombre="Lavado De Oído Felino", precio=15800),
    Procedimiento(nombre="Lavado De Oído Felino", precio=26300),

    # Limpieza de heridas
    Procedimiento(nombre="Limpieza De Herida Simple", precio=6300),
    Procedimiento(nombre="Limpieza De Herida Simple", precio=7400),

    # Mastectomía
    Procedimiento(nombre="Mastectomía Línea Completa", precio=12600),
    Procedimiento(nombre="Mastectomía Línea Completa", precio=63000),
    Procedimiento(nombre="Mastectomía Línea Completa", precio=73500),
    Procedimiento(nombre="Mastectomía Línea Completa", precio=74000),
    Procedimiento(nombre="Mastectomía Línea Completa", precio=84000),
    Procedimiento(nombre="Mastectomía Línea Completa", precio=100000),

    # Sedación
    Procedimiento(nombre="Sedación Canina A", precio=5300),
    Procedimiento(nombre="Sedación Canina B", precio=10000),
    Procedimiento(nombre="Sedación Canina C", precio=15800),
    Procedimiento(nombre="Sedación Felina A", precio=5300),
    Procedimiento(nombre="Sedación Felina B", precio=10500),

    # Quimioterapia
    Procedimiento(nombre="Sesión De Quimioterapia", precio=15800),
    Procedimiento(nombre="Sesión De Quimioterapia", precio=21000),
    Procedimiento(nombre="Sesión De Quimioterapia", precio=31500),

    # Sondaje
    Procedimiento(nombre="Sondaje Urinario Felino", precio=21000),
    Procedimiento(nombre="Sondaje Urinario Canino", precio=26300),
    Procedimiento(nombre="Sondaje Urinario Canino", precio=38000),
    Procedimiento(nombre="Sondaje Urinario Canino", precio=52500),
    Procedimiento(nombre="Sondaje Urinario Felino", precio=31500),

    # Sutura
    Procedimiento(nombre="Sutura", precio=47300),
    Procedimiento(nombre="Sutura Canina A", precio=15800),
    Procedimiento(nombre="Sutura Canina B", precio=30000),
    Procedimiento(nombre="Sutura Felina A", precio=15800),
    Procedimiento(nombre="Sutura Felina B", precio=36800),

    # Toma de muestras
    Procedimiento(nombre="Toma De Muestras Externas", precio=6300),
    Procedimiento(nombre="Toma De Muestras Sangre", precio=5300),

    # Tratamientos inyectables
    Procedimiento(nombre="Tratamiento Inyectable 5 A", precio=3200),
    Procedimiento(nombre="Tratamiento Inyectable 1 A", precio=2100),
    Procedimiento(nombre="Tratamiento Inyectable 1 A", precio=3700),
    Procedimiento(nombre="Tratamiento Inyectable 10", precio=3700),
    Procedimiento(nombre="Tratamiento Inyectable 10", precio=3700),
    Procedimiento(nombre="Tratamiento Inyectable 5 A", precio=4200),
    Procedimiento(nombre="Tratamiento Inyectable De", precio=4200),
    Procedimiento(nombre="Tratamiento Inyectable De", precio=5300),

    # Tumores
    Procedimiento(nombre="Tumores Canino A", precio=21000),
    Procedimiento(nombre="Tumores Canino B", precio=41000),
    Procedimiento(nombre="Tumores Caninos C", precio=61000),
    Procedimiento(nombre="Tumores Caninos D", precio=81000),
    Procedimiento(nombre="Tumores Caninos E", precio=105000),
    Procedimiento(nombre="Tumores Felino A", precio=21000),
    Procedimiento(nombre="Tumores Felino B", precio=52500),

    # Vacunas
    Procedimiento(nombre="Vacuna Antirrábica", precio=9500),
    Procedimiento(nombre="Vacuna Antirrábica", precio=11600),
    Procedimiento(nombre="Vacuna Óctuple SJ", precio=9500),
    Procedimiento(nombre="Vacuna Óctuple", precio=11600),
    Procedimiento(nombre="Vacuna Triple Felina", precio=10500),
    Procedimiento(nombre="Vacuna Triple Felina", precio=12600),

    # Vendajes
    Procedimiento(nombre="Vendaje Canino A", precio=15800),
    Procedimiento(nombre="Vendaje Canino B", precio=31500),
    Procedimiento(nombre="Vendaje Felino A", precio=10500),
    Procedimiento(nombre="Vendaje Felino B", precio=21000),
]


Procedimiento.objects.bulk_create(procedimientos)