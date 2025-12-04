import { Link } from 'react-router-dom'
import { ShoppingCart, User, Search, Menu } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const Header = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      {/* Top Bar */}
      <div className="bg-primary text-primary-foreground">
        <div className="container mx-auto px-4 py-2">
          <div className="flex justify-between items-center text-sm">
            <p>🚚 Free Delivery on Orders Over $50</p>
            <div className="flex gap-4">
              <Link to="/about" className="hover:underline">About</Link>
              <Link to="/contact" className="hover:underline">Contact</Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between gap-4">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="text-2xl font-bold text-primary">
              🌾 Farm2Door
            </div>
          </Link>

          {/* Search Bar */}
          <div className="hidden md:flex flex-1 max-w-xl">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Search for fresh products..."
                className="pl-10 w-full"
              />
            </div>
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-2">
            <Link to="/profile">
              <Button variant="ghost" size="icon">
                <User className="h-5 w-5" />
              </Button>
            </Link>

            <Link to="/cart">
              <Button variant="ghost" size="icon" className="relative">
                <ShoppingCart className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-primary text-xs text-primary-foreground flex items-center justify-center">
                  3
                </span>
              </Button>
            </Link>

            <Button variant="ghost" size="icon" className="md:hidden">
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Mobile Search */}
        <div className="md:hidden mt-4">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search products..."
              className="pl-10 w-full"
            />
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="border-t">
        <div className="container mx-auto px-4">
          <ul className="flex items-center gap-6 py-3 overflow-x-auto">
            <li>
              <Link to="/shop" className="text-sm font-medium hover:text-primary transition-colors">
                All Products
              </Link>
            </li>
            <li>
              <Link to="/shop?category=vegetables" className="text-sm font-medium hover:text-primary transition-colors">
                Vegetables
              </Link>
            </li>
            <li>
              <Link to="/shop?category=fruits" className="text-sm font-medium hover:text-primary transition-colors">
                Fruits
              </Link>
            </li>
            <li>
              <Link to="/shop?category=dairy" className="text-sm font-medium hover:text-primary transition-colors">
                Dairy
              </Link>
            </li>
            <li>
              <Link to="/shop?category=meat" className="text-sm font-medium hover:text-primary transition-colors">
                Meat & Poultry
              </Link>
            </li>
            <li>
              <Link to="/shop?category=organic" className="text-sm font-medium hover:text-primary transition-colors">
                Organic
              </Link>
            </li>
          </ul>
        </div>
      </nav>
    </header>
  )
}

export default Header
