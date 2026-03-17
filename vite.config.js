import { defineConfig } from 'vite';

export default defineConfig({
    build: {
        outDir: 'deeds/viteassets',
        assetsDir: '',
        rollupOptions: {
            input: 'src/main.js',
            output: {
                entryFileNames: 'main.js',
                chunkFileNames: '[name].js',
                assetFileNames: (assetInfo) => {
                    if (assetInfo.name && assetInfo.name.endsWith('.css')) {
                        return 'main.css';
                    }
                    return '[name][extname]';
                },
            },
        },
    },
});
