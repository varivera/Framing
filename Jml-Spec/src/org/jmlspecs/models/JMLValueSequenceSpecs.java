// @(#)$Id: JMLValueSequenceSpecs.java,v 1.19 2008/10/24 18:07:50 smshaner Exp $

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


package org.jmlspecs.models;
import java.math.BigInteger;


/** Specical behavior for JMLValueSequence not shared by JMLObjectSequence.
 *
 * @version $Revision: 1.19 $
 * @author Gary T. Leavens, with help from Clyde Ruby, and others.
 * @see JMLValueType
 * @see JMLValueBag
 */
//-@ immutable
// FIXME: adapt this file to non-null-by-default and remove the following modifier.
/*@ nullable_by_default @*/ 
public /*@ pure @*/ abstract class JMLValueSequenceSpecs
    implements JMLValueType
{

    /** Return the representative at the given index.
     *  @see #itemAt
     */
    /*@  public normal_behavior
      @   requires 0 <= i && i < int_length(); //FIXME, change to _length later
      @   ensures (* \result is the ith object of this *);
      @ public model JMLType objectAt(\bigint i);
      @*/

    // ********************** observers **************************

    /** Is the argument ".equals" to one of the values in this sequence.
     *  @see #has(Object)
     *  @see #int_count(JMLType)
     */
    /*@ public normal_behavior
      @   ensures \result <==>
      @         (* elem is ".equals" to one of the objects in this sequence *);
      @*/
    public abstract boolean has(JMLType elem);

    /** Is the argument ".equals" to one of the values in this sequence.
     *  @see #has(JMLType)
     *  @see #count(Object)
     */
    /*@   public normal_behavior
      @     requires elem != null;
      @     ensures \result
      @        <==> elem instanceof JMLType && has((JMLType)elem);
      @ also
      @   public normal_behavior
      @     requires elem == null;
      @     ensures \result == has(null);
      @*/    
    public boolean has(Object elem) {
        if (elem == null) {
            return has(null);
        } else {
            return elem instanceof JMLType && has((JMLType)elem);
        }
    }  

    /** Tell many times the argument occurs ".equals" to one of the
     * values in this sequence.
     *  @see #count(Object)
     *  @see #has(JMLType)
     */
    /*@ public normal_behavior
      @   ensures \result >= 0
      @       && (* \result is the number of times elem tests
      @              as ".equals" to one of the objects in this sequence *);
      @*/
    public abstract int count(JMLType elem);

    /** Tell many times the argument occurs ".equals" to one of the
     * values in the bag.
     *  @see #count(JMLType)
     *  @see #has(Object)
     */
    /*@   public normal_behavior
      @     requires elem != null;
      @     ensures \result
      @          == (elem instanceof JMLType ? count((JMLType)elem) : 0);
      @ also
      @   public normal_behavior
      @     requires elem == null;
      @     ensures \result == count(null);
      @*/    
    public int count(Object elem) {
        if (elem == null) {
            return count(null);
        } else {
            return (elem instanceof JMLType ? count((JMLType)elem) : 0);
        }
    }

    /** This sequence's length.
     */
    //@ public normal_behavior
    //@    ensures \result >= 0;
    public abstract int int_length();

    /** Return a clone of the element at the given zero-based index.
     *  @param i the zero-based index into the sequence.
     *  @exception JMLSequenceException if the index i is out of range.
     */
    public abstract /*@ nullable @*/ JMLType itemAt(int i)
        throws JMLSequenceException;

    /** Return a clone of the first element in this sequence.
     *  @exception JMLSequenceException if the sequence is empty.
     *  @see #last
     */
    public abstract /*@ nullable @*/ JMLType first()
        throws JMLSequenceException;

    /** Return a clone of the last element in this sequence.
     *  @exception JMLSequenceException if the sequence is empty.
     *  @see #first
     */
    public abstract /*@ nullable @*/ JMLType last()
        throws JMLSequenceException;

    // ********************** building new values *********

    /** Return a clone of this object, making clones of any contained
     *  objects in the sequence.
     */
    public abstract /*@ non_null @*/ Object clone();

    /** Return a sequence like this, but with a clone ofitem put
     *  immediately after the given index.
     *  @param afterThisOne a zero-based index into the sequence, or -1.
     *  @param item the item to put after index afterThisOne
     *  @return if the index is in range
     *  @exception JMLSequenceException if the index is out of range.
     *  @see #insertBeforeIndex
     *  @see #insertBack
     *  @see #insertFront
     */
    public abstract /*@ non_null @*/ JMLValueSequence
        insertAfterIndex(int afterThisOne, JMLType item)
        throws JMLSequenceException;

    /** Return a sequence like this, but with a clone of item put immediately
     *  before the given index.
     *  @param beforeThisOne a zero-based index into the sequence,
     *         or the length of this.
     *  @param item the item to put before index beforeThisOne
     *  @return if the index is in range
     *  @exception JMLSequenceException if the index is out of range.
     *  @see #insertAfterIndex
     *  @see #insertBack
     *  @see #insertFront
     */
    public abstract /*@ non_null @*/ JMLValueSequence
        insertBeforeIndex(int beforeThisOne, JMLType item)
        throws JMLSequenceException;


    /** Return a sequence like this, but with a clone of the given
     *  item put an the end.
     *  @param item the item to put at the end of the result.
     *  @return a sequence the elements of this sequence followed by item.
     *  @see #insertAfterIndex
     *  @see #insertBeforeIndex
     *  @see #insertFront
     */
    public abstract /*@ non_null @*/ JMLValueSequence insertBack(JMLType item);

    /** Return a sequence like this, but with the given item put an the front.
     *  @param item the item to put at the front of the result.
     *  @return a sequence with item followed by the elements of this sequence.
     *  @see #insertAfterIndex
     *  @see #insertBeforeIndex
     *  @see #insertBack
     */
    public abstract /*@ non_null @*/
        JMLValueSequence insertFront(JMLType item);
}
