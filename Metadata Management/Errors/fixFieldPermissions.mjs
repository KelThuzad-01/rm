import { promises as fs } from 'fs';
import path from 'path';

async function corregirFieldPermissions(rutaCarpeta) {
    try {
        // Leer todos los archivos en la carpeta
        const archivos = await fs.readdir(rutaCarpeta);

        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);
            let data = await fs.readFile(rutaArchivo, 'utf8');

            // Expresión regular para identificar bloques completos de <fieldPermissions>
            const fieldPermissionsRegex = /<fieldPermissions>[\s\S]*?<\/fieldPermissions>/g;

            let modificaciones = false;  // Bandera para saber si hay cambios

            // Modificar solo los bloques correctos
            let archivoModificado = data.replace(fieldPermissionsRegex, (match) => {
                if (match.includes('<editable>true</editable>') && match.includes('<readable>false</readable>')) {
                    modificaciones = true;
                    return match.replace('<readable>false</readable>', '<readable>true</readable>');
                }
                return match;  // Si no cumple la condición, no modifica
            });

            // Si hubo cambios, escribir el archivo modificado
            if (modificaciones) {
                await fs.writeFile(rutaArchivo, archivoModificado, 'utf8');
                console.log(`✅ Corregido en ${archivo}`);
            }
        }
    } catch (err) {
        console.error('❌ Error:', err);
    }
}

// Parámetro: ruta de la carpeta
const [,, rutaCarpeta] = process.argv;

corregirFieldPermissions(rutaCarpeta);
