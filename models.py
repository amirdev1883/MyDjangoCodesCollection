class Relation(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.from_user} follows {self.to_user}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(default=0)
    bio = models.TextField(null=True, blank=True)



class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    body = models.TextField()
    slug = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created', 'body']

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('home:post_detail', args=(self.id, self.slug))

    def like_count(self):
        return self.pvote.count()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ucomment')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='pcomment')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, related_name='rcomment', blank=True, null=True)
    is_reply = models.BooleanField(default=False)
    body = models.TextField(max_length=400)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.body[:30]}'


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uvote')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='pvote')

    def __str__(self):
        return f'{self.user} liked {self.post.slug}'
        
        
#------------------------------------------------------------------------------------------------------------------

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=225, unique=True)
    phone_number = models.CharField(max_length=11, unique=True)
    full_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    # Authenticate user with this fields
    REQUIRED_FIELDS = ['email', 'full_name']
    # this fields is just for superuser , when you use python manage.py createsuperuser

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin


class OtpCode(models.Model):
    phone_number = models.CharField(max_length=11, unique=True)
    code = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.phone_number} - {self.code} - {self.created}'
        


class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='scategory', null=True, blank=True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('home:category_filter', args=[self.slug])


class Product(models.Model):
    category = models.ManyToManyField(Category, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField()
    description = models.TextField()
    # price = models.DecimalField(max_digits=5, decimal_places=2)
    # 99999.99
    price = models.IntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('home:product_detail', args=[self.slug,])
        


class Order(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='orders')
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    discount = models.IntegerField(blank=True, null=True, default=None)

    class Meta:
        ordering = ('paid', '-updated')

    def __str__(self):
        return f'{self.user} - {str(self.id)}'

    def get_total_price(self):
        total = sum(item.get_cost() for item in self.items.all())
        if self.discount:
            discount_price = (self.discount / 100) * total
            return int(total - discount_price)
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price*self.quantity


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(90)])
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.code


#------------------------------------------------------------------------------------------------------------------


class Person(models.Model):
    name = models.CharField(max_length=30)
    age = models.SmallIntegerField()
    email = models.EmailField()

    def __str__(self):
        return self.name


class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.title[:20]}'


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.question.title[:20]}'



#-----------------------------------------------------------------------------------------------------------------------


class Post(BaseModel):

    slug = models.SlugField(
            primary_key=True,
            max_length=100,
    )
    title = models.CharField(
        max_length=100,
        unique=True,
    )
    content = models.CharField(
        max_length=1000,
    )
    author = models.ForeignKey(
            BaseUser, 
            on_delete=models.SET_NULL,
            null=True,
    )

    def __str__(self):
        return self.slug


class Subscription(models.Model):
    subscriber = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name="subs")
    target     = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name="targets")

    class Meta:
        unique_together = ('subscriber', 'target')

    def clean(self):
        if self.subscriber == self.target:
            raise ValidationError({"subscriber": ("subscriber cannot be equal to target")})

    def __str__(self):
        return f"{self.subscriber.email}- {self.target.email}"
        

class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RandomModel(BaseModel):
    """
    This is an example model, to be used as reference in the Styleguide,
    when discussing model validation via constraints.
    """
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="start_date_before_end_date",
                check=Q(start_date__lt=F("end_date"))
            )
        ]
        


class BaseUserManager(BUM):
    def create_user(self, email, is_active=True, is_admin=False, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email.lower()), is_active=is_active, is_admin=is_admin)

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email=email,
            is_active=True,
            is_admin=True,
            password=password,
        )

        user.is_superuser = True
        user.save(using=self._db)

        return user


class BaseUser(BaseModel, AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(verbose_name = "email address",
                              unique=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = BaseUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def is_staff(self):
        return self.is_admin


class Profile(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    posts_count = models.PositiveIntegerField(default=0)
    subscriber_count = models.PositiveIntegerField(default=0)
    subscription_count = models.PositiveIntegerField(default=0)
    bio = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return f"{self.user} >> {self.bio}"


