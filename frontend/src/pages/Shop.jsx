import { useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '@/components/common/Layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Filter, Search, Grid, List } from 'lucide-react'

const Shop = () => {
  const [viewMode, setViewMode] = useState('grid')
  const [selectedCategory, setSelectedCategory] = useState('all')

  const categories = [
    'All',
    'Vegetables',
    'Fruits',
    'Dairy',
    'Meat & Poultry',
    'Organic',
    'Bakery'
  ]

  const products = [
    { id: 1, name: 'Organic Tomatoes', price: 4.99, image: '🍅', category: 'Vegetables', rating: 4.5 },
    { id: 2, name: 'Fresh Strawberries', price: 6.99, image: '🍓', category: 'Fruits', rating: 5.0 },
    { id: 3, name: 'Farm Eggs', price: 5.99, image: '🥚', category: 'Dairy', rating: 4.8 },
    { id: 4, name: 'Green Lettuce', price: 3.49, image: '🥬', category: 'Vegetables', rating: 4.3 },
    { id: 5, name: 'Fresh Milk', price: 4.49, image: '🥛', category: 'Dairy', rating: 4.7 },
    { id: 6, name: 'Red Apples', price: 5.99, image: '🍎', category: 'Fruits', rating: 4.6 },
    { id: 7, name: 'Carrots', price: 2.99, image: '🥕', category: 'Vegetables', rating: 4.4 },
    { id: 8, name: 'Bananas', price: 3.99, image: '🍌', category: 'Fruits', rating: 4.5 },
    { id: 9, name: 'Broccoli', price: 3.99, image: '🥦', category: 'Vegetables', rating: 4.2 },
    { id: 10, name: 'Chicken Breast', price: 12.99, image: '🍗', category: 'Meat & Poultry', rating: 4.9 },
    { id: 11, name: 'Fresh Bread', price: 4.99, image: '🍞', category: 'Bakery', rating: 4.6 },
    { id: 12, name: 'Oranges', price: 5.49, image: '🍊', category: 'Fruits', rating: 4.7 }
  ]

  const filteredProducts = selectedCategory === 'all'
    ? products
    : products.filter(p => p.category.toLowerCase() === selectedCategory)

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Shop Fresh Products</h1>
          <p className="text-muted-foreground">Browse our selection of fresh, organic produce</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar Filters */}
          <aside className="lg:col-span-1">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Filter className="h-5 w-5" />
                  <h2 className="text-lg font-semibold">Filters</h2>
                </div>

                {/* Search */}
                <div className="mb-6">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input placeholder="Search products..." className="pl-10" />
                  </div>
                </div>

                {/* Categories */}
                <div className="mb-6">
                  <h3 className="font-semibold mb-3">Categories</h3>
                  <div className="space-y-2">
                    {categories.map((category) => (
                      <button
                        key={category}
                        onClick={() => setSelectedCategory(category.toLowerCase())}
                        className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                          selectedCategory === category.toLowerCase()
                            ? 'bg-primary text-primary-foreground'
                            : 'hover:bg-muted'
                        }`}
                      >
                        {category}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Price Range */}
                <div className="mb-6">
                  <h3 className="font-semibold mb-3">Price Range</h3>
                  <div className="space-y-2">
                    <Input type="number" placeholder="Min" />
                    <Input type="number" placeholder="Max" />
                    <Button className="w-full" variant="outline">Apply</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </aside>

          {/* Products Grid */}
          <div className="lg:col-span-3">
            {/* Toolbar */}
            <div className="flex items-center justify-between mb-6">
              <p className="text-sm text-muted-foreground">
                Showing {filteredProducts.length} products
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  size="icon"
                  onClick={() => setViewMode('grid')}
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  size="icon"
                  onClick={() => setViewMode('list')}
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Products */}
            <div className={viewMode === 'grid'
              ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'space-y-4'
            }>
              {filteredProducts.map((product) => (
                <Card key={product.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                  {viewMode === 'grid' ? (
                    <>
                      <div className="aspect-square bg-gradient-to-br from-green-100 to-green-50 flex items-center justify-center text-7xl">
                        {product.image}
                      </div>
                      <CardContent className="p-4">
                        <p className="text-xs text-muted-foreground mb-1">{product.category}</p>
                        <h3 className="font-semibold mb-2">{product.name}</h3>
                        <div className="flex items-center gap-1 mb-3">
                          <span className="text-yellow-500">★</span>
                          <span className="text-sm">{product.rating}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-2xl font-bold text-primary">${product.price}</span>
                          <div className="flex gap-2">
                            <Link to={`/product/${product.id}`}>
                              <Button size="sm">View</Button>
                            </Link>
                          </div>
                        </div>
                      </CardContent>
                    </>
                  ) : (
                    <div className="flex items-center p-4 gap-4">
                      <div className="w-24 h-24 bg-gradient-to-br from-green-100 to-green-50 flex items-center justify-center text-5xl rounded-md">
                        {product.image}
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-muted-foreground mb-1">{product.category}</p>
                        <h3 className="font-semibold mb-1">{product.name}</h3>
                        <div className="flex items-center gap-1 mb-2">
                          <span className="text-yellow-500">★</span>
                          <span className="text-sm">{product.rating}</span>
                        </div>
                        <span className="text-xl font-bold text-primary">${product.price}</span>
                      </div>
                      <div className="flex gap-2">
                        <Link to={`/product/${product.id}`}>
                          <Button>View Details</Button>
                        </Link>
                      </div>
                    </div>
                  )}
                </Card>
              ))}
            </div>

            {/* Pagination */}
            <div className="flex justify-center gap-2 mt-8">
              <Button variant="outline">Previous</Button>
              <Button variant="outline">1</Button>
              <Button>2</Button>
              <Button variant="outline">3</Button>
              <Button variant="outline">Next</Button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default Shop
