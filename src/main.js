import Alpine from 'alpinejs';

window.Alpine = Alpine;

Alpine.start();

import Quill from 'quill/dist/quill.js';
import 'quill/dist/quill.snow.css';

window.Quill = Quill;

document.addEventListener('DOMContentLoaded', () => {
  const editor = document.querySelector('#editor');
  if (editor) {
    const quill = new Quill('#editor', {
      theme: 'snow',
      placeholder: 'Write your post here...',
      modules: {
        toolbar: [
          [{ header: [1, 2, 3, false] }],
          ['bold', 'italic', 'underline'],
          [{ align: [] }],
          ['clean']
        ]
      }
    });

    const contentInput = document.querySelector('input[name="content"]');
    if (contentInput) {
      // If editing, preload the editor content
      if (contentInput.value) {
        quill.root.innerHTML = contentInput.value;
      }

      // Sync editor content to hidden input on form submit
      document.querySelector('form').addEventListener('submit', () => {
        contentInput.value = quill.root.innerHTML;
      });
    }
  }
});
import './main.css';
