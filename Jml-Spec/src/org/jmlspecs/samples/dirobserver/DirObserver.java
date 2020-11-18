// @(#)$Id: DirObserver.java 1199 2009-02-17 19:42:32Z smshaner $

// Copyright (C) 2001 Iowa State University

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

package org.jmlspecs.samples.dirobserver;

//@ model import org.jmlspecs.models.*;

/** Observers (i.e. listeners) in the directory system. */
public interface DirObserver {

    /** The state of this observer. */
    //@ public model instance JMLDataGroup obsState;

    /** Receive a notification that a given name is being added
     *  to the given directory.
     */ 
    /*@ public normal_behavior
      @   requires o != null && o.in_notifier && n != null && !n.equals("");
      @   assignable obsState;
      @   ensures o.equals(\old(o));
      @*/
    void addNotification(Directory o, String n);

    /** Receive a notification that a given name is being removed
     *  from the given directory.
     */ 
    /*@ public normal_behavior
      @   requires o != null && o.in_notifier && n != null && !n.equals("");
      @   assignable obsState;
      @   ensures o.equals(\old(o));
      @*/
    void removeNotification(Directory o, String n);
}
