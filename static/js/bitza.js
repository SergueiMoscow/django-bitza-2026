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

  /*
   * Функция удаляет обработчики событий к элементам модального окна при закрытии
   */
const detachModalEvents = () => {
    modal.querySelector(".close").removeEventListener("click", closeModal);
    document.removeEventListener("keydown", handleEscape);
    modal.removeEventListener("click", handleOutside);
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

let modal = document.querySelector("#myModal");

const attachModalEvents = () => {
    // закрывать модальное окно при нажатии на крестик
    modal.querySelector(".close").addEventListener("click", closeModal);
    // закрывать модальное окно при нажатии клавиши Escape
    document.addEventListener("keydown", handleEscape);
    // закрывать модальное окно при клике вне контента модального окна
    modal.addEventListener("click", handleOutside);
};


document.addEventListener("DOMContentLoaded", () => {
  modal = document.querySelector("#myModal");
  const contractSearch = document.querySelector("#search-contract");
  const paymentSearch = document.querySelector("#search-payment");
  const contactSearch = document.querySelector("#search-contact");

  const openModal = () => {
    modal.classList.add("modal-open");
    // обработчики событий, которые работают, когда окно открыто
    attachModalEvents();
  };

  if (document.querySelector("#editBtn")) {
    document.querySelector("#editBtn").addEventListener("click", openModal);
  }


  if (contractSearch != null) {
    contractSearch.addEventListener("keyup", (event) => {
      if (contractSearch.value.length > 2) {
        ajax({
          method: "GET",
          url: "/rent/contracts?container=div&q=" + contractSearch.value,
          success: (response) => {
            div = document.getElementById("list_contracts");
            div.innerHTML = response;
          },
        });
      }
    });
  };

  if (paymentSearch != null) {
    paymentSearch.addEventListener("keyup", (event) => {
      if (paymentSearch.value.length > 2) {
        ajax({
          method: "GET",
          url: "/rent/payments?container=div&q=" + paymentSearch.value,
          success: (response) => {
            div = document.getElementById("list_payments");
            div.innerHTML = response;
          },
        });
      }
    });
  };

  if (contactSearch != null) {
    contactSearch.addEventListener("keyup", (event) => {
      if (contactSearch.value.length > 2) {
        ajax({
          method: "GET",
          url: "/rent/clients?container=div&q=" + contactSearch.value,
          success: (response) => {
            div = document.getElementById("list_contacts");
            div.innerHTML = response;
          },
        });
      }
    });
  };

});

close_contract = (id) => {
  ajax({
    method: "GET",
    url: `/rent/close_contract?contract=${id}`,
    success: (response) => {
        modal = document.getElementById("myModal");
        modal_content = document.getElementById("modal_content");
        modal_content.innerHTML = response;
        modal.classList.add("modal-open");
        // окно закрыто, эти обработчики событий больше не нужны
        attachModalEvents();
    },
 });}