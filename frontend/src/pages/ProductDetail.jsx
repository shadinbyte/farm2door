import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '@/components/common/Layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Minus, Plus, ShoppingCart, Heart, Share2, Star, Truck, Shield } from 'lucide-react'

const ProductDetail = () => {
  const { id } = useParams()
  const [quantity, setQuantity] = useState(1)
  const [selectedImage, setSelectedImage] = useState(0)

  // Mock product data - in real app, fetch from API
  const product = {
    id: id,
    name: 'Organic Tomatoes',
    price: 4.99,
    image: '🍅',
    category: 'Vegetables',
    rating: 4.5,
    reviews: 128,
    description: 'Fresh, juicy organic tomatoes grown locally without pesticides. Perfect for salads, sauces, and cooking. Hand-picked at peak ripeness to ensure maximum flavor and nutrition.',
    inStock: true,
    stock: 45,
    weight: '1 lb',
    origin: 'Local Farm, California',
    certifications: ['USDA Organic', 'Non-GMO']
  }

  const relatedProducts = [
    { id: 4, name: 'Green Lettuce', price: 3.49, image: '🥬' },
    { id: 7, name: 'Carrots', price: 2.99, image: '🥕' },
    { id: 9, name: 'Broccoli', price: 3.99, image: '🥦' }
  ]

  const handleQuantityChange = (type) => {
    if (type === 'increment' && quantity < product.stock) {
      setQuantity(quantity + 1)
    } else if (type === 'decrement' && quantity > 1) {
      setQuantity(quantity - 1)
    }
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <nav className="mb-6 text-sm">
          <Link to="/" className="text-muted-foreground hover:text-primary">Home</Link>
          <span className="mx-2">/</span>
          <Link to="/shop" className="text-muted-foreground hover:text-primary">Shop</Link>
          <span className="mx-2">/</span>
          <span>{product.category}</span>
          <span className="mx-2">/</span>
          <span className="text-foreground">{product.name}</span>
        </nav>

        {/* Product Details */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Product Images */}
          <div>
            <Card className="overflow-hidden mb-4">
              <div className="aspect-square bg-gradient-to-br from-green-100 to-green-50 flex items-center justify-center text-9xl">
                {product.image}
              </div>
            </Card>
            <div className="grid grid-cols-4 gap-2">
              {[0, 1, 2, 3].map((index) => (
                <Card
                  key={index}
                  className={`cursor-pointer overflow-hidden ${selectedImage === index ? 'ring-2 ring-primary' : ''}`}
                  onClick={() => setSelectedImage(index)}
                >
                  <div className="aspect-square bg-gradient-to-br from-green-100 to-green-50 flex items-center justify-center text-4xl">
                    {product.image}
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* Product Info */}
          <div>
            <div className="mb-4">
              <p className="text-sm text-muted-foreground mb-2">{product.category}</p>
              <h1 className="text-4xl font-bold mb-4">{product.name}</h1>

              {/* Rating */}
              <div className="flex items-center gap-2 mb-4">
                <div className="flex items-center">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      className={`h-5 w-5 ${
                        star <= Math.floor(product.rating)
                          ? 'fill-yellow-500 text-yellow-500'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-sm text-muted-foreground">
                  {product.rating} ({product.reviews} reviews)
                </span>
              </div>

              {/* Price */}
              <div className="mb-6">
                <span className="text-4xl font-bold text-primary">${product.price}</span>
                <span className="text-muted-foreground ml-2">/ {product.weight}</span>
              </div>

              {/* Description */}
              <p className="text-muted-foreground mb-6">{product.description}</p>

              {/* Product Details */}
              <div className="space-y-3 mb-6">
                <div className="flex justify-between py-2 border-b">
                  <span className="text-muted-foreground">Origin:</span>
                  <span className="font-medium">{product.origin}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-muted-foreground">Availability:</span>
                  <span className={`font-medium ${product.inStock ? 'text-green-600' : 'text-red-600'}`}>
                    {product.inStock ? `In Stock (${product.stock} units)` : 'Out of Stock'}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-muted-foreground">Certifications:</span>
                  <span className="font-medium">{product.certifications.join(', ')}</span>
                </div>
              </div>

              {/* Quantity Selector */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Quantity</label>
                <div className="flex items-center gap-4">
                  <div className="flex items-center border rounded-md">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleQuantityChange('decrement')}
                      disabled={quantity <= 1}
                    >
                      <Minus className="h-4 w-4" />
                    </Button>
                    <span className="px-6 font-medium">{quantity}</span>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleQuantityChange('increment')}
                      disabled={quantity >= product.stock}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    Subtotal: <span className="font-bold text-foreground">${(product.price * quantity).toFixed(2)}</span>
                  </span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 mb-6">
                <Button size="lg" className="flex-1">
                  <ShoppingCart className="mr-2 h-5 w-5" />
                  Add to Cart
                </Button>
                <Button size="lg" variant="outline">
                  <Heart className="h-5 w-5" />
                </Button>
                <Button size="lg" variant="outline">
                  <Share2 className="h-5 w-5" />
                </Button>
              </div>

              {/* Features */}
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardContent className="flex items-center gap-3 p-4">
                    <Truck className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-semibold text-sm">Free Delivery</p>
                      <p className="text-xs text-muted-foreground">On orders over $50</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="flex items-center gap-3 p-4">
                    <Shield className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-semibold text-sm">Quality Guarantee</p>
                      <p className="text-xs text-muted-foreground">100% Fresh</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>

        {/* Related Products */}
        <div>
          <h2 className="text-3xl font-bold mb-6">You May Also Like</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {relatedProducts.map((item) => (
              <Card key={item.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <div className="aspect-square bg-gradient-to-br from-green-100 to-green-50 flex items-center justify-center text-7xl">
                  {item.image}
                </div>
                <CardContent className="p-4">
                  <h3 className="font-semibold mb-2">{item.name}</h3>
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold text-primary">${item.price}</span>
                    <Link to={`/product/${item.id}`}>
                      <Button size="sm">View</Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default ProductDetail
