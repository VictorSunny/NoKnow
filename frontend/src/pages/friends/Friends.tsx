import { AnimatePresence } from "framer-motion";
import React, { useState } from "react";
import AnimatedWindowWrapper from "../AnimatedWindowWrapper";
import { Outlet } from "react-router-dom";
import { Link } from "react-router-dom";

import "./Friends.css";
import { NavLink } from "react-router-dom";
import NavContainer from "../../components/general/dropdownSelect/NavContainer";

export default function Friends() {
  return (
    <div className="page-container friends-page-container">
      <NavContainer>
        <nav className="window-nav">
          <NavLink className="nav-link" to={"/friends"} end replace>
            friends
          </NavLink>
          <NavLink className="nav-link" to={"/friends/requests"} end replace>
            pending
          </NavLink>
          <NavLink className="nav-link" to={"/friends/sent"} end replace>
            requested
          </NavLink>
        </nav>
      </NavContainer>
      <div className="page-main-content grow">
        <AnimatePresence mode="wait">
          <AnimatedWindowWrapper key={location.pathname}>
            <Outlet />
          </AnimatedWindowWrapper>
        </AnimatePresence>
      </div>
    </div>
  );
}
