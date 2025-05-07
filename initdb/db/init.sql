CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(15) NOT NULL
);

CREATE TABLE IF NOT EXISTS amigos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    amigo_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (amigo_id) REFERENCES usuarios(id),
    CONSTRAINT unique_amigos UNIQUE (usuario_id, amigo_id),
    CHECK (usuario_id <> amigo_id)
);

INSERT INTO usuarios (nombre, telefono) VALUES
('Juan', '612345678'),
('Ana', '613456789'),
('Luis', '614567890'),
('María', '615678901'),
('Carlos', '616789012'),
('Marco', '617890123'),
('Antonia', '618901234'),
('Pepe', '619012345'),
('Jose', '620123456'),
('Sofía', '621234567'),
('Pedro', '622345678'),
('Lucía', '623456789'),
('Diego', '624567890'),
('Elena', '625678901'),
('Andrés', '626789012');

INSERT INTO amigos (usuario_id, amigo_id) VALUES
(6,7),
(6,8),
(6,9),
(2,8),
(1,9),
(10,11),
(11,12),
(12,13),
(13,14),
(14,15),
(1,2),
(3,4),
(5,10),
(7,11),
(8,12),
(9,13);
