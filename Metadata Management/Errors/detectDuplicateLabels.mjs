import { promises as fs } from 'fs';
import path from 'path';

// Obtener la ruta del archivo desde los argumentos
const [, , rutaArchivo] = process.argv;

if (!rutaArchivo) {
    console.error("❌ No se proporcionó la ruta del archivo. Uso: node detectDuplicateLabels.mjs <rutaArchivo>");
    process.exit(1);
}

async function detectarCustomLabelsDuplicados(rutaArchivo) {
    try {
        const contenido = await fs.readFile(rutaArchivo, 'utf8');

        // Expresión regular para capturar fullName y language
        const regex = /<labels>\s*<fullName>(.*?)<\/fullName>[\s\S]*?<language>(.*?)<\/language>/g;
        const etiquetas = new Map();
        let match;
        let duplicados = [];

        while ((match = regex.exec(contenido)) !== null) {
            const fullName = match[1];
            const language = match[2];
            const key = `${fullName}::${language}`; // Clave única combinando nombre y lenguaje

            if (etiquetas.has(key)) {
                duplicados.push(fullName);
            } else {
                etiquetas.set(key, true);
            }
        }

        if (duplicados.length > 0) {
            console.log("🚨 **Detectados Custom Labels duplicados (mismo fullName y language)**:");
            [...new Set(duplicados)].forEach(label => console.log(` - ${label}`));
        } else {
            console.log("✅ No se encontraron etiquetas duplicadas.");
        }
    } catch (error) {
        console.error("❌ Error leyendo el archivo:", error);
    }
}

// Ejecutar función con la ruta proporcionada
detectarCustomLabelsDuplicados(rutaArchivo);
