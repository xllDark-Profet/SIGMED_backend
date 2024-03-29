use sigmed;

INSERT INTO Especialidad (id, nombre) VALUES (1, 'Cardiología');
INSERT INTO Especialidad (id, nombre) VALUES (2, 'Pediatría');
INSERT INTO Especialidad (id, nombre) VALUES (3, 'Neurología');
INSERT INTO Especialidad (id, nombre) VALUES (4, 'Oncología');
INSERT INTO Especialidad (id, nombre) VALUES (5, 'Ginecología');
-- Sigue con otras especialidades según sea necesario

-- Insertar datos en la tabla Hospital
INSERT INTO Hospital (id, nombre, codigo_registro, latitud, longitud) VALUES (1, 'Hospital Infantil Universitario San Jose', 'HC123', '4.665224548607437', '-74.07896502839728');
INSERT INTO Hospital (id, nombre, codigo_registro, latitud, longitud) VALUES (2, 'Hospital Engativa', 'HN456', '4.711001914622836', '-74.1097278695707');
INSERT INTO Hospital (id, nombre, codigo_registro, latitud, longitud) VALUES (3, 'Unidad de Servicios de Salud Simón Bolívar', 'IN789', '4.742781005353155', '-74.02301609413335');
INSERT INTO Hospital (id, nombre, codigo_registro, latitud, longitud) VALUES (4, 'Hospital Universitario Nacional de Colombia', 'CON101', '4.648789324522056', '-74.09552777693953');
INSERT INTO Hospital (id, nombre, codigo_registro, latitud, longitud) VALUES (5, 'Hospital de Kennedy', 'CGM202', '4.61657176477835', '-74.15332014004682');

-- Continuación de INSERTs en la tabla Hospital_Especialidad
INSERT INTO Hospital_Especialidad (hospital_id, especialidad_id) VALUES (3, 1);
INSERT INTO Hospital_Especialidad (hospital_id, especialidad_id) VALUES (3, 4);
INSERT INTO Hospital_Especialidad (hospital_id, especialidad_id) VALUES (4, 2);
INSERT INTO Hospital_Especialidad (hospital_id, especialidad_id) VALUES (4, 5);
INSERT INTO Hospital_Especialidad (hospital_id, especialidad_id) VALUES (5, 1);
INSERT INTO Hospital_Especialidad (hospital_id, especialidad_id) VALUES (5, 2);
INSERT INTO Hospital_Especialidad (hospital_id, especialidad_id) VALUES (5, 3);
INSERT INTO Hospital_Especialidad (hospital_id, especialidad_id) VALUES (5, 4);
INSERT INTO Hospital_Especialidad (hospital_id, especialidad_id) VALUES (5, 5);
INSERT INTO Hospital_Especialidad (hospital_id, especialidad_id) VALUES (2, 5);
INSERT INTO Hospital_Especialidad (hospital_id, especialidad_id) VALUES (1, 4);
INSERT INTO Hospital_Especialidad (hospital_id, especialidad_id) VALUES (2, 3);
