 const products=[
                {
                    id:1,
                    name:"classical chair everlastic Design",
                    price:120,
                    image:"chair.jpeg",
                    slug: "classical-chair-everlastic-design",

                },
                {
                    id:2,
                    name:"Chair sewel",
                    price:151,
                    image:"item2.jpeg",
                    slug: "chair-sewel",

                },
                {
                    id:3,
                    name:"Modern styl etta",
                    price:181,
                    image:"item3.jpeg",
                    slug: "modern-styl-etta",

                },
                {
                    id:4,
                    name:"Sony 3d TV",
                    price:150,
                    image:"item4.jpeg",
                    slug: "sony-3d-tv",

                },
                {
                    id:5,
                    name:"mountain bike hercules",
                    price:200,
                    image:"item5.jpeg",
                    slug: "mountain-bike-hercules",

                },
                {
                    
                    id:6,
                    name:"Redmi note 10 lite",
                    price:110,
                    image:"item6.jpeg",
                    slug: "redmi-note-10-lite",

                
                },
            ];

            let cart=[];

            function searchProducts(){
                let query=document.getElementById("search").value.toLowerCase();
                let filtered=products.filter((product)=>{
                   return  product.name.toLowerCase().includes(query);
                  
                });
                  displayProducts(filtered);
            }

            function displayProducts(filtered=products){
                let productDiv=document.getElementById("products");
                productDiv.innerHTML="";
                filtered.forEach((product)=>{
                    let productContainer=document.createElement("div");
                    productContainer.classList.add("product");
                    productContainer.innerHTML=` 
                     <img class="img1" src="${product.image}" alt=""/>
                <p class="p1">${product.name}</p>
                <p class="p2">${product.price}</p>
                <button class="add" onclick="addTocart(${product.id})">Add to Cart</button>`;
                productDiv.appendChild(productContainer);
                });
            }

            function addTocart(id){
                let selectedProduct=products.find((product)=>product.id===id);
                let existingItem=cart.find((product)=>product.id===id);


                if(existingItem)
                {
                    existingItem.quantity++;
                }
                else{
                    cart.push({...selectedProduct,quantity:1});
                }
                
                updateCart();
            }
            function updateCart(){
                let  cartDiv=document.getElementById("cart-c");
                cartDiv.innerHTML="";
                
                let totalAount=0;

                if(cart.length===0)
                {
                    cartDiv.innerHTML="<p>Your cart is empty</p>";
                    document.getElementById("total").textContent="Total:$0";
                    localStorage.removeItem("cart");
                    return;

                }

                cart.forEach((item,index)=>{
                    let cartItem=document.createElement("div");
                    cartItem.classList.add("cart-p");

                    totalAount+=item.price*item.quantity;

                    cartItem.innerHTML=`
                        <img src="${item.image}" alt="${item.name}">
                    <p>${item.name}-${item.price}</p>
                    <input type="number" min="1" value="${item.quantity}" onchange="updateQuantity(${index},this.value)"/>
                    <button onclick="remove(${index})">Remove</button>
                    `;
                    cartDiv.appendChild(cartItem);


                });

                document.getElementById("total").textContent=`Total:${totalAount}`;
                localStorage.setItem("cart",JSON.stringify(cart));

            }
            window.addEventListener("DOMContentLoaded",()=>{
                const storedCart=localStorage.getItem("cart");
                if(storedCart){
                    cart=JSON.parse(storedCart);
                    updateCart();

                }
            })


            function remove(index){
                cart.splice(index,1);
                updateCart();
            }

            function updateQuantity(index,quantity){
                cart[index].quantity=Math.max(1,quantity);
                updateCart();
            }

            displayProducts();

            function toggleCart(){
                const cart=document.querySelector(".cart");
                const toggleBtn=document.getElementById("cart-toggle-btn");
                cart.classList.toggle("open");
            }
           