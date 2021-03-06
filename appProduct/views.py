from register.models import UserProfile
from typing import cast
from django.forms.models import modelform_factory
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Size, Color, Gender, ImageProduct, Variants, Post
from .forms import ProductForm, VariantsForm,ImageProductForm,PostForm
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.template.loader import render_to_string, get_template
from django.views.decorators.csrf import csrf_protect
from order.models import Order, Cart
from django.db.models import Q
from .filters import ProductFilter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import random


# Create your views here.


def product(request):
    # products = Product.objects.all()
    product_list = Product.objects.all()
    categorys = Category.objects.all()
    genders = Gender.objects.all()
    variants = Variants.objects.all()
    
    page = request.GET.get('page', 1)
    paginator = Paginator(product_list, 12)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    if request.GET:
        productFilter = ProductFilter(request.GET, queryset=product_list)
        product_list = productFilter.qs

        page = request.GET.get('page', 1)
        paginator = Paginator(product_list, 12)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        return render(request, 'product/product.html', {'products': products, 'productFilter': productFilter,'categorys': categorys, 'genders': genders,'variants': variants})
    return render(request, 'product/product.html', {'products': products, 'categorys': categorys, 'genders': genders,})

# search_ajax


def searchProduct(request):
    if request.method == "GET":
        search_text = request.GET['search_text']
        if search_text is not None and search_text != u"":
            search_text = request.GET['search_text']
    else:
        search_text = ''
    product_list = Product.objects.filter(name__contains=search_text)

    page = request.GET.get('page', 1)
    paginator = Paginator(product_list, 12)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return render(request, 'product/ajax_search.html', {'products': products})


@login_required
def productuser(request):
    variants = Variants.objects.all()
    productlist = Product.objects.filter(user=request.user)
    page = request.GET.get('page', 1)
    paginator = Paginator(productlist, 12)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return render(request, 'product/productuser.html', {'products': products, 'variants': variants})


@login_required
def createproduct(request):
    # ở đây không dùng ajax
    # if request.method == "GET":
    #     categorys = Category.objects.all()
    #     return render(request, 'product/createproduct.html', {'form': ProductForm(), 'categorys': categorys})
    # else:
    #     form = ProductForm(request.POST)
    #     product = form.save(commit=False)
    #     product.user = request.user
    #     category = str(request.POST['category'])
    #     product.category = Category.objects.filter(name = category)[0]
    #     product.save()
    #     return redirect('appProduct:productuser')

    # -------------------------------------------------------------------------------------------

    # ở đây dùng ajax
    # categorys = Category.objects.all()
    # if request.is_ajax(): #nếu như yêu cầu nhận được là ajax
    #     categorys = Category.objects.all()
    #     form = ProductForm(request.POST)
    #     product = form.save(commit=False)
    #     product.user = request.user
    #     if 'image' in request.FILES:
    #         product.image = request.FILES['image']
    #     category = str(request.POST['category'])
    #     product.category = Category.objects.filter(name = category)[0]
    #     product.save()
    #     return JsonResponse({'response':"Success"})
    # return render(request, 'product/createproduct.html', {'form': ProductForm(), 'categorys': categorys, 'variantsForm': VariantsForm()})

    # ---------------------------------------------------------------------------------------------

    categorys = Category.objects.all()
    genders = Gender.objects.all()
    sizes = Size.objects.all()
    colors = Color.objects.all()
    imageProductList = ImageProduct.objects.filter(user=request.user)
    if request.is_ajax():  # nếu như yêu cầu nhận được là ajax
        # form
        formVariants = VariantsForm(request.POST, prefix="variantsForm")
        formProduct = ProductForm(
            request.POST, prefix="productForm")  # nhập dữ liệu từ form
        if formProduct.is_valid() and formVariants.is_valid():
            product = formProduct.save(commit=False)  # lữa dữ liệu form tạm
            product.user = request.user  # lưu thông tin người tạo ra sản phẩm
            if 'productForm-image' in request.FILES:
                 product.image = request.FILES['productForm-image']
            # category = str(request.POST['category'])  #lấy category
            # product.category = Category.objects.filter(name = category)[0] #lưa category vừa lấy vào product
            product.save()  # lưa dữ liệu lên database

            # varitsform
            variant = formVariants.save(commit=False)
            product.gender = variant.gender
            product.save()
            variant.product = product
            variant.save()
            variants = Variants.objects.get(product=product)
            sizelist = request.POST.getlist('variantsForm-size', None)
            colorlist = request.POST.getlist('variantsForm-color', None)
            imagelist = request.POST.getlist('variantsForm-imageProduct', None)
            counter = 0
            for image in imagelist:
                image_pk = imagelist.__getitem__(counter)
                image_entity = ImageProduct.objects.get(pk=image_pk)
                image_entity.product = product
                image_entity.save()
                variants.imageProduct.add(image_entity)
                counter += 1
            counter = 0
            for size in sizelist:
                size_pk = sizelist.__getitem__(counter)
                size_entity = Size.objects.get(pk=size_pk)
                variants.size.add(size_entity)
                counter += 1
            counter = 0
            for color in colorlist:
                color_pk = colorlist.__getitem__(counter)
                color_entity = Color.objects.get(pk=color_pk)
                variants.color.add(color_entity)
                counter += 1
            return JsonResponse({})
        else:
            return JsonResponse({'responsive': "fail"})
    return render(request, 'product/createproduct.html', {'formProduct': ProductForm(prefix="productForm"), 'variantsForm': VariantsForm(prefix="variantsForm"),'ImageProductForm':ImageProductForm(prefix="ImageProductForm") ,'categorys': categorys,'genders': genders, 'sizes': sizes, 'colors': colors, 'imageProductList': imageProductList})
    
    
@login_required
def editproduct(request, product_pk):
    # if request.method == "GET":
    #     form = ProductForm(instance=product)
    #     categorys = Category.objects.all()
    #     return render(request, 'product/editproduct.html', {'product' : product , 'form': form, 'categorys': categorys})
    # else:
    #     category = str(request.POST['category'])
    #     product.category = Category.objects.filter(name = category)[0]
    #     if 'image' in request.FILES:
    #         product.image = request.FILES['image']
    #     product.save()
    #     form = ProductForm(request.POST, instance = product)
    #     form.save()
    #     return redirect('appProduct:productuser')

    # ajax edit
    # form = ProductForm(instance=product)
    # categorys = Category.objects.all()
    # if request.is_ajax():
    #     category = str(request.POST['category'])
    #     product.category = Category.objects.filter(name=category)[0]
    #     if 'image' in request.FILES:
    #         product.image = request.FILES['image']
    #     product.save()
    #     form = ProductForm(request.POST, instance=product)
    #     form.save()
    #     return JsonResponse({'response': "Success"})
    # else:
    #     return render(request, 'product/editproduct.html', {'product': product, 'form': form, 'categorys': categorys})
    
    
    product = get_object_or_404(Product, pk=product_pk, user=request.user)
    try:
        variant = Variants.objects.get(product = product)
    except Variants.DoesNotExist:
        variant = None
    formProduct = ProductForm(instance=product,prefix="productForm")
    formVariant = VariantsForm(instance=variant, prefix="variantsForm")
    categorys = Category.objects.all()
    genders = Gender.objects.all()
    sizes = Size.objects.all()
    colors = Color.objects.all()
    variantSize={}
    variantColor={}
    variantImageProduct={}
    if variant:
        variantSize = variant.size.all()
        variantColor = variant.color.all()
        variantImageProduct = variant.imageProduct.all()
    imageProductList = ImageProduct.objects.filter(user=request.user)
    if request.is_ajax():
        categoryid = request.POST['productForm-category']
        product.category = Category.objects.get(id=categoryid)
        if 'productForm-image' in request.FILES:
            product.image = request.FILES['productForm-image']
        product.save()
        formProduct = ProductForm(request.POST, instance=product, prefix="productForm")
        formProduct.save()
        
        genderid = request.POST['variantsForm-gender']
        if variant:
            variant.gender = Gender.objects.get(id=genderid)
            product.gender = variant.gender
            product.save()
            sizelist = request.POST.getlist('variantsForm-size', None)
            colorlist = request.POST.getlist('variantsForm-color', None)
            imagelist = request.POST.getlist('variantsForm-imageProduct', None)
            variant.imageProduct.clear()
            variant.size.clear()
            variant.color.clear()
            imagelist.pop(0)
            counter = 0
            for image in imagelist:
                image_pk = imagelist.__getitem__(counter)
                image_entity = ImageProduct.objects.get(pk=image_pk)
                image_entity.product = product
                image_entity.save()
                variant.imageProduct.add(image_entity)
                counter += 1
            counter = 0
            for size in sizelist:
                size_pk = sizelist.__getitem__(counter)
                size_entity = Size.objects.get(pk=size_pk)
                variant.size.add(size_entity)
                counter += 1
            counter = 0
            for color in colorlist:
                color_pk = colorlist.__getitem__(counter)
                color_entity = Color.objects.get(pk=color_pk)
                variant.color.add(color_entity)
                counter += 1
            variant.save()  
            # formVariant = VariantsForm(request.POST ,instance=variant, prefix="variantsForm")
            # formVariant.save()
        else:
            if formVariant:
                variant = formVariant.save(commit=False)
                product.gender = variant.gender
                product.save()
                variant.product = product
                variant.save()
                variants = Variants.objects.get(product=product)
                sizelist = request.POST.getlist('variantsForm-size', None)
                colorlist = request.POST.getlist('variantsForm-color', None)
                imagelist = request.POST.getlist('variantsForm-imageProduct', None)
                imagelist.pop(0)
                counter = 0
                for image in imagelist:
                    image_pk = imagelist.__getitem__(counter)
                    image_entity = ImageProduct.objects.get(pk=image_pk)
                    image_entity.product = product
                    image_entity.save()
                    variants.imageProduct.add(image_entity)
                    counter += 1
                counter = 0
                for size in sizelist:
                    size_pk = sizelist.__getitem__(counter)
                    size_entity = Size.objects.get(pk=size_pk)
                    variants.size.add(size_entity)
                    counter += 1
                counter = 0
                for color in colorlist:
                    color_pk = colorlist.__getitem__(counter)
                    color_entity = Color.objects.get(pk=color_pk)
                    variants.color.add(color_entity)
                    counter += 1
        return JsonResponse({'response': "Success"})
    else:
        return render(request, 'product/editproduct.html', {'product': product,'variant':variant,'categorys': categorys,'genders': genders,'sizes':sizes,'colors':colors,'imageProductList':imageProductList,'variantSize':variantSize,'variantColor':variantColor,'variantImageProduct':variantImageProduct, 'formProduct': formProduct,'formVariant':formVariant,'ImageProductForm':ImageProductForm(prefix="ImageProductForm") ,})


@login_required
def deleteproduct(request, product_pk):
    # product = get_object_or_404(Product, pk=product_pk, user=request.user) #lấy thông tin todo nếu ko có trả về 404
    # if request.method == "POST":
    #     product.delete()
    #     return redirect('appProduct:productuser')

    # ở đây dùng ajax
    product = get_object_or_404(Product, pk=product_pk, user=request.user)
    product.delete()
    data = {
        'deleted': True
    }
    return JsonResponse(data)


def detailproduct(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    try:
        variant = Variants.objects.get(product = product)
    except Variants.DoesNotExist:
        variant = None
    if variant:
        variantSize = variant.size.all()
        variantColor = variant.color.all()
        variantImageProduct = variant.imageProduct.all()[:12]
        variantGender = variant.gender
    else:
        variantSize = None
        variantColor=None
        variantImageProduct=None
        variantGender = "Null"
    comments=Post.objects.filter(product=product_pk)
    return render(request, 'product/detailproduct.html', {'product': product, 'variant': variant, 'variantSize': variantSize, 'variantColor': variantColor, 'variantImageProduct': variantImageProduct, 'variantGender': variantGender, 'comments': comments})


@login_required
def createimageproduct(request):
    if request.method == 'POST':
        form = ImageProductForm(request.POST,request.FILES, prefix="ImageProductForm", )
        if form.is_valid():
            imageProduct = form.save(commit=False)
            imageProduct.user = request.user
            if 'ImageProductForm-image' in request.FILES:
                imageProduct.image = request.FILES['ImageProductForm-image']
            imageProduct.save()
        imageProductList = ImageProduct.objects.filter(user = request.user)
        return render(request, 'product/createimageproduct.html', {'imageProductList' : imageProductList})  
    
@login_required
def editcreateimageproduct(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk, user=request.user)
    try:
        variant = Variants.objects.get(product = product)
    except Variants.DoesNotExist:
        variant = None
    if variant:
        variantImageProduct = variant.imageProduct.all()
    else:
        variantImageProduct = None
    if request.method == 'POST':
        form = ImageProductForm(request.POST,request.FILES, prefix="ImageProductForm", )
        if form.is_valid():
            imageProduct = form.save(commit=False)
            imageProduct.user = request.user
            if 'ImageProductForm-image' in request.FILES:
                imageProduct.image = request.FILES['ImageProductForm-image']
            imageProduct.save()
        imageProductList = ImageProduct.objects.filter(user = request.user)
        return render(request, 'product/createimageproduct.html', {'imageProductList' : imageProductList, 'variantImageProduct':variantImageProduct,'variant': variant})    
    
    
def getnamecolor(request, product_pk):
    if request.is_ajax():
        if request.POST.get('id') == "None":
            return JsonResponse({'name': "None"})
        color = Color.objects.get(id=request.POST.get('id'))
        return JsonResponse({'name': color.name})
    
    
def getnameSize(request, product_pk):
    if request.is_ajax():
        size = Size.objects.get(id=request.POST.get('id'))
        return JsonResponse({'name': size.name})
    
def getnameSizeCreate(request):
    if request.is_ajax():
        size = Size.objects.get(id=request.POST.get('id'))
        return JsonResponse({'name': size.name})
    
def getnameColorCreate(request):
    if request.is_ajax():
        color = Color.objects.get(id=request.POST.get('id'))
        return JsonResponse({'name': color.name})
    
    
def getnameSizeEdit(request, product_pk):
    if request.is_ajax():
        size = Size.objects.get(id=request.POST.get('id'))
        return JsonResponse({'name': size.name})
    
def getnameColorEdit(request, product_pk):
    if request.is_ajax():
        color = Color.objects.get(id=request.POST.get('id'))
        return JsonResponse({'name': color.name})
    
@login_required
def addcomment(request, product_pk):
    if request.is_ajax:
        form=PostForm(request.POST)
        if form.is_valid():
            data= form.save(commit=False)
            data.content=form.cleaned_data['content']
            data.subject=form.cleaned_data['subject']
            data.user=request.user
            product=Product.objects.get(pk=product_pk)
            data.product=product
            data.userProfile = UserProfile.objects.get(user = request.user)
            data.save()
            comments=Post.objects.filter(product=product_pk)
            return render(request, 'product/addcomment.html', {'comments' :comments})  
        else :
            return HttpResponse('khong dung dinh dang')
    comments=Post.objects.filter(product=product_pk)
    return  render(request, 'product/detailproduct.html', {'comments' :comments})
