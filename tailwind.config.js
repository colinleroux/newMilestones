/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./deeds/templates/**/*.html"],
  theme: {
    extend: {
      fontFamily: {
        handwritten: ['"Dancing Script"', 'cursive'],
        redhat: ['"Red Hat Display", sans-serif'],
      },
    },
  },
  plugins: [],
}
