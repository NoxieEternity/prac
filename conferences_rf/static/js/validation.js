/* Клиентская проверка регистрации и автоматический слайдер. */
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector('[data-validate="register"]');
  if (form) {
    const rules = {
      login: [v => /^[A-Za-z][A-Za-z0-9_]{3,19}$/.test(v), "От 4 до 20 символов: латиница, цифры и _."],
      password: [v => v.length >= 6, "Пароль должен содержать не менее 6 символов."],
      full_name: [v => /^[А-Яа-яЁё -]+$/.test(v) && v.trim().split(/\s+/).length >= 2, "Введите фамилию и имя русскими буквами."],
      phone: [v => /^8\(\d{3}\)\d{3}-\d{2}-\d{2}$/.test(v), "Формат: 8(900)123-45-67."],
      email: [v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v), "Введите корректный e-mail."]
    };
    const validate = input => {
      const rule = rules[input.name];
      if (!rule) return true;
      const ok = rule[0](input.value.trim());
      const error = form.querySelector(`[data-error="${input.name}"]`);
      if (error) error.textContent = ok ? "" : rule[1];
      input.classList.toggle("is-invalid", !ok);
      return ok;
    };
    Object.keys(rules).forEach(name => {
      const input = form.elements[name];
      if (input) input.addEventListener("blur", () => validate(input));
    });
    form.addEventListener("submit", event => {
      const valid = Object.keys(rules).map(name => validate(form.elements[name])).every(Boolean);
      if (!valid) event.preventDefault();
    });
  }

  document.querySelectorAll("[data-confirm]").forEach(button => {
    button.addEventListener("click", event => {
      if (!window.confirm(button.dataset.confirm)) event.preventDefault();
    });
  });

  const slider = document.querySelector("[data-slider]");
  if (slider) {
    const slides = [...slider.querySelectorAll(".slide")];
    const dots = [...slider.querySelectorAll(".slider__dot")];
    let current = 0;
    const show = index => {
      current = index;
      slides.forEach((slide, i) => slide.classList.toggle("is-active", i === current));
      dots.forEach((dot, i) => dot.classList.toggle("is-active", i === current));
    };
    dots.forEach((dot, i) => dot.addEventListener("click", () => show(i)));
    window.setInterval(() => show((current + 1) % slides.length), 5000);
  }
});
