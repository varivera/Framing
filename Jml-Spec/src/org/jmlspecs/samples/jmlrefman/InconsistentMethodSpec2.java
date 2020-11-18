// @(#)$Id: InconsistentMethodSpec2.java 1199 2009-02-17 19:42:32Z smshaner $

// Copyright (C) 2005 Iowa State University

// This file is part of JML

// JML is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2, or (at your option)
// any later version.

// JML is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with JML; see the file COPYING.  If not, write to
// the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.


package org.jmlspecs.samples.jmlrefman;

public abstract class InconsistentMethodSpec2 {

    /** A specification that can't be satisfied. */
    /*@  public exceptional_behavior
     @     requires z < 99;
     @     assignable \nothing;
     @     signals_only IllegalArgumentException;
     @ also
     @   public exceptional_behavior
     @     requires z > 0;
     @     assignable \nothing;
     @     signals_only NullPointerException;
     @*/
    public abstract int cantBeSatisfied(int z)
        throws IllegalArgumentException, NullPointerException;
}
