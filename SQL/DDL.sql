use sigmed;

CREATE TABLE Especialidad (
    id INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE Hospital (
    id INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo_registro VARCHAR(50) NOT NULL,
    latitud VARCHAR(100) NOT NULL,
    longitud VARCHAR(100) NOT NULL
);

CREATE TABLE Hospital_Especialidad (
    hospital_id INT,
    especialidad_id INT,
    FOREIGN KEY (hospital_id) REFERENCES Hospital(id),
    FOREIGN KEY (especialidad_id) REFERENCES Especialidad(id),
    PRIMARY KEY (hospital_id, especialidad_id)
);