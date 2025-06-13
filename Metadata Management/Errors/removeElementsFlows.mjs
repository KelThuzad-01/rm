import { promises as fs } from 'fs';
import path from 'path';

async function eliminarLineaExacta(rutaCarpeta, lineaAEliminar) {
    try {
        const archivos = await fs.readdir(rutaCarpeta);

        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);

            // Verificamos que sea archivo .xml
            if (path.extname(archivo).toLowerCase() !== '.xml') continue;

            const data = await fs.readFile(rutaArchivo, 'utf8');

            const lineas = data.split('\n');
            const lineasFiltradas = lineas.filter(linea => linea.trim() !== lineaAEliminar.trim());

            if (lineas.length !== lineasFiltradas.length) {
                await fs.writeFile(rutaArchivo, lineasFiltradas.join('\n'), 'utf8');
                console.log(`Línea eliminada en: ${archivo}`);
            }
        }
    } catch (err) {
        console.error('Error al procesar archivos:', err);
    }
}

// Uso: node script.mjs "<línea-a-eliminar>" <ruta-carpeta>
const [,, lineaAEliminar, rutaCarpeta] = process.argv;

if (!lineaAEliminar || !rutaCarpeta) {
    console.error('Uso: node script.mjs "<línea-a-eliminar>" <ruta-carpeta>');
    process.exit(1);
}

eliminarLineaExacta(rutaCarpeta, lineaAEliminar);
