// @(#)$Id: shortAbstractIterator.java-generic,v 1.7 2005/12/24 21:20:31 chalin Exp $

// Copyright (C) 2005 Iowa State University
//
// This file is part of the runtime library of the Java Modeling Language.
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public License
// as published by the Free Software Foundation; either version 2.1,
// of the License, or (at your option) any later version.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with JML; see the file LesserGPL.txt.  If not, write to the Free
// Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
// 02110-1301  USA.

package org.jmlspecs.jmlunit.strategies;

/** Common code for iterators over values of type short that
 * implement the ShortIterator interface.
 * @author Gary T. Leavens
 */
public abstract class ShortAbstractIterator
    implements ShortIterator
{

    // doc comment and specification inherited
    public /*@ nullable @*/ Object get() {
        return new Short(getShort());
    }

    public /*@ pure @*/ Object clone() {
        try {
            return super.clone();
        } catch (CloneNotSupportedException e) {
            //@ unreachable;
            throw new InternalError(e.toString());
        }
    }
}
