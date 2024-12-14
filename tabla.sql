CREATE TABLE "Portafolio_de_prueba" (
	"id"	INTEGER,
	"accion"	TEXT,
	"sector"	TEXT,
	"ticket"	TEXT NOT NULL UNIQUE,
	"dinero_invertido"	REAL,
	"precio_promedio_compra"	REAL,
	"cantidad_nominales"	INTEGER,
	"fecha_compra"	TEXT,
	"precio_actual"	REAL,
	"valor_actual"	REAL,
	PRIMARY KEY("id" AUTOINCREMENT)
);