import { useNavigationContext } from '../contexts/NavigationContext'
import { useEffect } from 'react'

export default function useSetPageTitle(pageTitle: string | undefined) {
  const {currentPageTitle, setCurrentPageTitle} = useNavigationContext()
  useEffect(() => {
    setCurrentPageTitle(pageTitle)
  }, [])
  return currentPageTitle
}
