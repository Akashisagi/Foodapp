const menuGrid = document.querySelector("#menu-grid");
const categoryTabs = document.querySelector("#category-tabs");
const cartItems = document.querySelector("#cart-items");
const itemCount = document.querySelector("#item-count");
const orderTotal = document.querySelector("#order-total");
const menuCount = document.querySelector("#menu-count");
const placeOrderButton = document.querySelector("#place-order");
const checkoutForm = document.querySelector("#checkout-form");
const formMessage = document.querySelector("#form-message");
const cart = new Map();
let menu = [];
let activeCategory = "All";

const money = (amount) => new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
}).format(amount);

function renderCategories() {
  const categories = ["All", ...new Set(menu.map((item) => item.category))];
  categoryTabs.innerHTML = categories.map((category) => `
    <button class="category-tab ${category === activeCategory ? "is-active" : ""}" type="button" data-category="${category}" aria-pressed="${category === activeCategory}">
      ${category}<span>${category === "All" ? menu.length : menu.filter((item) => item.category === category).length}</span>
    </button>
  `).join("");
  categoryTabs.addEventListener("click", (event) => {
    const button = event.target.closest("[data-category]");
    if (!button) return;
    activeCategory = button.dataset.category;
    renderCategories();
    renderMenu();
  }, { once: true });
}

function renderMenu() {
  const visibleItems = activeCategory === "All"
    ? menu
    : menu.filter((item) => item.category === activeCategory);
  menuCount.textContent = `${visibleItems.length} good things to try`;
  menuGrid.innerHTML = visibleItems.map((item) => `
    <article class="menu-item">
      <div class="menu-image-wrap">
        <img class="menu-image" src="${item.image}" alt="${item.name}" loading="lazy">
        <span class="menu-tag">${item.tag}</span>
      </div>
      <div class="menu-item-info">
        <div>
          <p class="menu-category">${item.category}</p>
          <h3>${item.name}</h3>
        </div>
        <button class="add-button" type="button" data-add="${item.id}" aria-label="Add ${item.name} to your order">+</button>
      </div>
      <p class="menu-description">${item.description}</p>
      <p class="menu-price">${money(item.price)}</p>
    </article>
  `).join("");
}

function renderCart() {
  const entries = [...cart.values()];
  const count = entries.reduce((sum, entry) => sum + entry.quantity, 0);
  const total = entries.reduce((sum, entry) => sum + entry.item.price * entry.quantity, 0);
  itemCount.textContent = count;
  orderTotal.textContent = money(total);
  placeOrderButton.disabled = entries.length === 0;

  if (!entries.length) {
    cartItems.innerHTML = `
      <div class="empty-cart">
        <span class="empty-cart-mark" aria-hidden="true">+</span>
        <p>Your table is waiting.</p>
        <span>Add something from the menu to get started.</span>
      </div>`;
    return;
  }

  cartItems.innerHTML = entries.map(({ item, quantity }) => `
    <div class="cart-row">
      <div class="cart-row-main">
        <span class="cart-quantity">${quantity}×</span>
        <div><strong>${item.name}</strong><span>${money(item.price * quantity)}</span></div>
      </div>
      <div class="quantity-controls" aria-label="Quantity for ${item.name}">
        <button type="button" data-change="${item.id}" data-step="-1" aria-label="Remove one ${item.name}">−</button>
        <span>${quantity}</span>
        <button type="button" data-change="${item.id}" data-step="1" aria-label="Add one ${item.name}">+</button>
      </div>
    </div>
  `).join("");
}

menuGrid.addEventListener("click", (event) => {
  const button = event.target.closest("[data-add]");
  if (!button) return;
  const item = menu.find((entry) => entry.id === Number(button.dataset.add));
  const current = cart.get(item.id)?.quantity ?? 0;
  if (current >= 20) return;
  cart.set(item.id, { item, quantity: current + 1 });
  renderCart();
  formMessage.textContent = "";
});

cartItems.addEventListener("click", (event) => {
  const button = event.target.closest("[data-change]");
  if (!button) return;
  const id = Number(button.dataset.change);
  const entry = cart.get(id);
  const quantity = entry.quantity + Number(button.dataset.step);
  if (quantity < 1) cart.delete(id);
  else cart.set(id, { ...entry, quantity });
  renderCart();
});

checkoutForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!cart.size) return;
  placeOrderButton.disabled = true;
  placeOrderButton.querySelector("span").textContent = "Sending...";
  formMessage.classList.remove("is-error");
  formMessage.textContent = "";

  const formData = new FormData(checkoutForm);
  const payload = {
    customer_name: formData.get("customer_name"),
    table_number: Number(formData.get("table_number")),
    items: [...cart.values()].map(({ item, quantity }) => ({
      menu_item_id: item.id,
      quantity,
    })),
  };

  try {
    const response = await fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "We couldn't send your order.");
    cart.clear();
    renderCart();
    checkoutForm.reset();
    formMessage.textContent = `Order #${result.order_id} sent. Thank you, ${payload.customer_name.trim()}!`;
  } catch (error) {
    formMessage.textContent = error.message;
    formMessage.classList.add("is-error");
  } finally {
    placeOrderButton.querySelector("span").textContent = "Send to the kitchen";
    placeOrderButton.disabled = cart.size === 0;
  }
});

async function startApp() {
  const tableSelect = document.querySelector("#table-number");
  for (let table = 1; table <= 20; table += 1) {
    tableSelect.add(new Option(`Table ${table}`, table));
  }

  try {
    const response = await fetch("/api/menu");
    if (!response.ok) throw new Error("Menu is unavailable right now.");
    menu = await response.json();
    renderCategories();
    renderMenu();
  } catch (error) {
    menuGrid.innerHTML = `<p class="loading-message">${error.message} Please refresh to try again.</p>`;
  }
}

startApp();