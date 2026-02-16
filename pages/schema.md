# Database Schema
~~~sql
CREATE TABLE "grid" (
   ident TEXT PRIMARY KEY NOT NULL,
   size INTEGER NOT NULL,
   spacing REAL NOT NULL,
   lat0 REAL NOT NULL,
   lon0 REAL NOT NULL
, "image" BLOB)
CREATE TABLE grid_cells (
   grid_id TEXT REFERENCES grid(ident),
   lat REAL,
   lon REAL,
   value REAL,
   PRIMARY KEY (grid_id, lat, lon)
)
CREATE TABLE "machine" (
   ident TEXT PRIMARY KEY NOT NULL,
   name TEXT NOT NULL
)
CREATE TABLE "person" (
   ident TEXT PRIMARY KEY NOT NULL,
   family TEXT NOT NULL,
   personal TEXT NOT NULL,
   supervisor_id TEXT REFERENCES person(ident)
)
CREATE TABLE "rating" (
   person_id TEXT NOT NULL REFERENCES person(ident),
   machine_id TEXT NOT NULL REFERENCES machine(ident),
   certified INTEGER NOT NULL
)
CREATE TABLE "assay" (
   ident TEXT PRIMARY KEY NOT NULL,
   lat REAL NOT NULL REFERENCES grid_cells(lat),
   lon REAL NOT NULL REFERENCES grid_cells(lon),
   person_id TEXT NOT NULL REFERENCES person(ident),
   machine_id TEXT NOT NULL REFERENCES machine(ident),
   performed TEXT
)
CREATE TABLE assay_readings (
   assay_id TEXT REFERENCES assay(ident),
   reading_id INTEGER,
   contents TEXT,
   reading REAL,
   PRIMARY KEY (assay_id, reading_id)
)
CREATE TABLE "species" (
   reference TEXT NOT NULL,
   susc_locus INTEGER NOT NULL,
   susc_base TEXT NOT NULL
)
CREATE TABLE species_loci (
   ident INTEGER PRIMARY KEY,
   locus INTEGER
)
CREATE TABLE "specimen" (
   ident TEXT NOT NULL,
   lat REAL NOT NULL,
   lon REAL NOT NULL,
   genome TEXT NOT NULL,
   mass REAL NOT NULL,
   diameter REAL NOT NULL,
   collected TEXT,
   variety TEXT
)
~~~
