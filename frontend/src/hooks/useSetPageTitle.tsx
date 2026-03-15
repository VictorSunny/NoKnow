import { useLocation } from 'react-router-dom'
import { useNavigationContext } from '../contexts/NavigationContext'
import React, { useEffect } from 'react'

export default function useSetPageTitle(pageTitle: string | undefined) {
  const {currentPageTitle, setCurrentPageTitle} = useNavigationContext()
  const location = useLocation()
  useEffect(() => {
    setCurrentPageTitle(pageTitle)
  }, [])
  return currentPageTitle
}
