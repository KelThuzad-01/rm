import { promises as fs } from 'fs';

// Obtener la ruta del archivo desde los argumentos
const [, , rutaArchivo] = process.argv;

if (!rutaArchivo) {
    console.error("❌ No se proporcionó la ruta del archivo. Uso: node removeDuplicateLabels.mjs <rutaArchivo>");
    process.exit(1);
}

async function eliminarCustomLabelsDuplicados(rutaArchivo) {
    try {
        let contenido = await fs.readFile(rutaArchivo, 'utf8');

        // Expresión regular para capturar bloques completos de <labels>
        const regex = /(<labels>\s*<fullName>(.*?)<\/fullName>\s*<categories>(.*?)<\/categories>\s*<language>(.*?)<\/language>\s*<protected>(.*?)<\/protected>\s*<shortDescription>(.*?)<\/shortDescription>\s*<value>(.*?)<\/value>\s*<\/labels>)/gs;

        const etiquetasUnicas = new Set();
        let contenidoLimpio = contenido;
        let eliminados = [];

        let match;
        while ((match = regex.exec(contenido)) !== null) {
            const bloqueCompleto = match[1]; // Captura todo el bloque <labels>...</labels>
            const identificador = match[2] + "::" + match[4] + "::" + match[6] + "::" + match[7]; // Clave única con valores

            if (etiquetasUnicas.has(identificador)) {
                contenidoLimpio = contenidoLimpio.replace(bloqueCompleto, ''); // Eliminar duplicado
                eliminados.push(match[2]); // Guardar el fullName eliminado
            } else {
                etiquetasUnicas.add(identificador);
            }
        }

        // Eliminar líneas en blanco adicionales
        contenidoLimpio = contenidoLimpio.replace(/^\s*[\r\n]/gm, '');

        if (eliminados.length > 0) {
            console.log("🚨 **Se eliminaron Custom Labels duplicados:**");
            eliminados.forEach(label => console.log(` - ${label}`));

            // Guardar el archivo limpio
            await fs.writeFile(rutaArchivo, contenidoLimpio.trim(), 'utf8');
            console.log("✅ Archivo actualizado correctamente (líneas en blanco eliminadas).");
        } else {
            console.log("✅ No se encontraron etiquetas duplicadas.");
        }

    } catch (error) {
        console.error("❌ Error procesando el archivo:", error);
    }
}

// Ejecutar función con la ruta proporcionada
eliminarCustomLabelsDuplicados(rutaArchivo);
