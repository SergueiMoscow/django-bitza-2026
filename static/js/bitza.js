const ajax = (args = {}) => {
  let method = "POST";
  if (args.method) {
    method = args.method;
  }
  const responseType = args.responseType || "text";
  const defaultError = (event) => {
    alert(`Error: ${event}`);
  };
  const xhr = new XMLHttpRequest();
  let params = "";
  if (args.data) {
    params = new URLSearchParams(args.data).toString();
  }
  xhr.open(method, args.url, true);
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  if (args.headers) {
    Object.entries(args.headers).forEach((entry) => {
      [key, value] = entry;
      xhr.setRequestHeader(key, value);
    });
  }
  xhr.responseType = responseType;
  console.log(`Ajax (${method}) ${args.url} p: ${params}`);
  xhr.send(params);
  xhr.onload = function () {
    args.success(xhr.response);
  };
  if (args.error) {
    xhr.onerror = function () {
      args.error(xhr.response);
    };
  } else {
    xhr.onerror = defaultError;
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.querySelector("#myModal");
  const inputSearch = document.querySelector("#search-contract");

  const openModal = () => {
    modal.classList.add("modal-open");
    // обработчики событий, которые работают, когда окно открыто
    attachModalEvents();
  };

  if (document.querySelector("#editBtn")) {
    document.querySelector("#editBtn").addEventListener("click", openModal);
  }

  const attachModalEvents = () => {
    // закрывать модальное окно при нажатии на крестик
    modal.querySelector(".close").addEventListener("click", closeModal);
    // закрывать модальное окно при нажатии клавиши Escape
    document.addEventListener("keydown", handleEscape);
    // закрывать модальное окно при клике вне контента модального окна
    modal.addEventListener("click", handleOutside);
  };

  /*
   * Обработчик события клика по кнопке закрытия модального окна
   */
  const closeModal = () => {
    modal.classList.remove("modal-open");
    // окно закрыто, эти обработчики событий больше не нужны
    detachModalEvents();
  };

  /*
   * Функция удаляет обработчики событий к элементам модального окна при закрытии
   */
  const detachModalEvents = () => {
    modal.querySelector(".close").removeEventListener("click", closeModal);
    document.removeEventListener("keydown", handleEscape);
    modal.removeEventListener("click", handleOutside);
  };

  /*
   * Функция закрывает модальное окно при нажатии клавиши Escape
   */
  const handleEscape = (event) => {
    if (event.key === "Escape") {
      closeModal();
    }
  };

  /*
   * Функция закрывает модальное окно при клике вне контента модального окна
   */
  const handleOutside = (event) => {
    const isClickInside =
      !!event.target.closest(".modal-content") ||
      event.target.parentElement.className == "autocomplete-items";
    if (!isClickInside) {
      closeModal();
    }
  };

  if (inputSearch != null) {
    inputSearch.addEventListener("keyup", (event) => {
      if (inputSearch.value.length > 2) {
        ajax({
          method: "GET",
          url: "/rent/contracts?container=div&q=" + inputSearch.value,
          success: (response) => {
            div = document.getElementById("list_contracts");
            div.innerHTML = response;
          },
        });
      }
    });
  }
});
