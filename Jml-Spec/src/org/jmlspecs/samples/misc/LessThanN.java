// @(#)$Id: LessThanN.java 1199 2009-02-17 19:42:32Z smshaner $

// Copyright (C) 1998, 1999 Iowa State University

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

package org.jmlspecs.samples.misc;

/** A search problem which is to find the first number strictly less
 * than n (and greater than 0).
 * @author Gary T. Leavens
 */
public class LessThanN extends SingleSolution
{
    /** Initialize this search problem. */
    //@ requires n > 0;
    //@ ensures this.n == n;
    public LessThanN(int n) {
        super(n);
    }

    // doc comment inherited
    //@ also
    //@ requires j >= 0;
    //@ ensures \result <==> j < n;
    public /*@ pure @*/ boolean f(int j) {
        return j < n;
    }

    // doc comment and specification inherited
    protected String className() {
        return "LessThanN";
    }
}
