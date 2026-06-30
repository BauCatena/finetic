-- 1. Categories Table
CREATE TABLE IF NOT EXISTS categories (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "incidentThreshold" INTEGER DEFAULT 0
);

-- 2. Neighborhoods Table
CREATE TABLE IF NOT EXISTS neighborhoods (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "name" VARCHAR(150) NOT NULL,
    "geometryLocation" TEXT 
);

-- 3. Trackers (Pets) Table
CREATE TABLE IF NOT EXISTS trackers (
    id UUID PRIMARY KEY,
    "deviceId" VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    breed VARCHAR(100),
    "animalType" VARCHAR(50),
    "previousIncidents" INT,
    description TEXT,
    vaccines TEXT,          -- 👈 ¡AGREGÁ ESTA LÍNEA ACÁ!
    age INT,
    "categoryId" UUID
);

-- 4. Users Table
CREATE TABLE IF NOT EXISTS users (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "name" VARCHAR(150) NOT NULL,
    "address" TEXT,
    "trackerId" UUID REFERENCES trackers("id") ON DELETE SET NULL,
    "neighborhoodId" UUID REFERENCES neighborhoods("id") ON DELETE SET NULL,
    "categoryId" UUID REFERENCES categories("id") ON DELETE SET NULL
);

-- 5. Recent Locations Table (Last 8/12 hours)
CREATE TABLE IF NOT EXISTS recentLocations (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "trackerId" UUID REFERENCES trackers("id") ON DELETE CASCADE,
    "latitude" NUMERIC(10, 7) NOT NULL,
    "longitude" NUMERIC(10, 7) NOT NULL,
    "trackerTimestamp" TIMESTAMP WITH TIME ZONE NOT NULL,
    "signalType" VARCHAR(10), -- GPRS or GPS
    "rawHex" TEXT NOT NULL,    -- Storing raw packet data for debugging
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seeder de Categoría
INSERT INTO categories ("id", "name", "description", "incidentThreshold")
VALUES ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Normal', 'Monitoreo estándar', 0);

-- Seeder de Barrio
INSERT INTO neighborhoods ("id", "name", "geometryLocation")
VALUES ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Palermo', '-34.5889, -58.4304');

-- Seeder del Rastreador
-- NOTA: Recordá que el 'deviceId' debe ser el IMEI/Serial que tu GPS mande en el paquete de Login (0x01)
INSERT INTO trackers ("id", "deviceId", "name", "breed", "animalType", "previousIncidents", "description", "vaccines", "age", "categoryId")
VALUES (
    'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 
    '868022030666221', -- Cambialo por tu IMEI real de pruebas
    'Firulais', 
    'Ovejero Alemán', 
    'Perro', 
    0, 
    'Rastreador de pruebas', 
    'Sextuple, Rabia', -- Campo vacunas
    3, -- Edad
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
);

-- Seeder del Dueño (Usuario)
INSERT INTO users ("id", "name", "address", "trackerId", "neighborhoodId", "categoryId")
VALUES (
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a44', 
    'Juan Pérez', 
    'Av. Santa Fe 1234', 
    'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 
    'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
);