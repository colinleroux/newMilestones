import { defineConfig } from 'vite';

export default defineConfig({
    build: {
        outDir: 'deeds/viteassets', // Output directory for compiled assets
        assetsDir: '',         // Place all assets directly inside 'dist'
        rollupOptions: {
            input: 'src/main.js', // Correct path to main.js
        },
    },
});
