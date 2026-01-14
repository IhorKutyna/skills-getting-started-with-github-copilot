document.addEventListener('click', (event) => {
  if (event.target.classList.contains('delete-btn')) {
    const email = event.target.getAttribute('data-email');
    // Logic to unregister the participant
    console.log(`Unregistering participant: ${email}`);
    // Here you would typically make a fetch call to your backend to unregister the participant
  }
});