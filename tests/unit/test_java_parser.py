import pytest
from src.parsers.java_parser import JavaParser, FunctionDescription


@pytest.fixture
def parser():
    return JavaParser()


def test_simple_method(parser):
    java_code = """
    public class Test {
        /** Simple method */
        public int sum(int a, int b) {
            return a + b;
        }
    }
    """
    funcs = parser.parse_content(java_code)
    assert len(funcs) == 1
    f = funcs[0]
    assert f.name == "sum"
    assert f.parameters == ["int a", "int b"]
    assert f.return_type == "int"
    assert f.has_body
    assert f.docstring == "Simple method"
    assert f.qualified_name == "Test.sum"


def test_nested_generics(parser):
    java_code = """
    public class GenericClass {
        public <T, U> T identity(U value) { return null; }
    }
    """
    funcs = parser.parse_content(java_code)
    assert len(funcs) == 1
    f = funcs[0]
    assert f.name == "identity"
    assert f.parameters == ["U value"]
    assert f.return_type == "T"
    assert f.has_body


def test_varargs(parser):
    java_code = """
    public class VarArgsTest {
        public void printAll(String... args) {}
    }
    """
    funcs = parser.parse_content(java_code)
    f = funcs[0]
    assert f.parameters == ["String... args"]
    assert f.has_body


def test_nested_classes(parser):
    java_code = """
    public class Outer {
        public static class Inner {
            public void innerMethod() {}
        }
    }
    """
    funcs = parser.parse_content(java_code)
    f = funcs[0]
    assert f.qualified_name == "Outer.Inner.innerMethod"


def test_interface_methods(parser):
    java_code = """
    public interface MyInterface {
        void abstractMethod();

        default void defaultMethod() {}

        static void staticMethod(String... args) {}

        private void privateMethod() {}
    }
    """
    funcs = parser.parse_content(java_code)
    names = {f.name: f for f in funcs}

    # abstract method
    assert not names["abstractMethod"].has_body
    assert "abstract" in names["abstractMethod"].modifiers

    # default method
    assert names["defaultMethod"].has_body
    assert "default" in names["defaultMethod"].modifiers

    # static method
    assert names["staticMethod"].has_body
    assert "static" in names["staticMethod"].modifiers
    assert names["staticMethod"].parameters == ["String... args"]

    # private method
    assert names["privateMethod"].has_body
    assert "private" in names["privateMethod"].modifiers


def test_docstrings_and_annotations(parser):
    java_code = """
    public class AnnotatedTest {
        /**
         * Multi-line comment
         */
        @Deprecated
        public void oldMethod() {}
    }
    """
    funcs = parser.parse_content(java_code)
    f = funcs[0]
    assert f.docstring == "Multi-line comment"
    assert "@Deprecated" in f.decorators
    assert f.has_body


def test_complex_nested(parser):
    java_code = """
    public class Outer<T> {
        public void outerMethod(T param) {}
        public static class Inner {
            public <U> U innerMethod(U param) throws Exception { return param; }
        }
        public interface InnerInterface {
            void abstractMethod();
            default void defaultMethod() {}
            static void staticMethod(String... args) {}
            private void privateMethod() {}
        }
    }
    """
    funcs = parser.parse_content(java_code)
    # Проверяем qualified_name
    expected_names = [
        "Outer.outerMethod",
        "Outer.Inner.innerMethod",
        "Outer.InnerInterface.abstractMethod",
        "Outer.InnerInterface.defaultMethod",
        "Outer.InnerInterface.staticMethod",
        "Outer.InnerInterface.privateMethod"
    ]
    assert [f.qualified_name for f in funcs] == expected_names

    # Проверяем varargs
    static_method = next(f for f in funcs if f.name == "staticMethod")
    assert static_method.parameters == ["String... args"]

    # Проверяем nested generics
    inner_method = next(f for f in funcs if f.name == "innerMethod")
    assert inner_method.parameters == ["U param"]
    assert inner_method.return_type == "U"

    # Проверяем abstract/default/static/private методы интерфейса
    iface_methods = {f.name: f for f in funcs if "Interface" in f.class_name}
    assert not iface_methods["abstractMethod"].has_body
    assert iface_methods["defaultMethod"].has_body
    assert iface_methods["staticMethod"].has_body
    assert iface_methods["privateMethod"].has_body

def test_javadoc_parsing(parser):
    java_code = """
    public class LinkedList<E> {
        /**
         * Получает узел по указанному индексу.
         *
         * @param index индекс узла, который нужно получить. Индекс должен быть неотрицательным и соответствовать позиции узла в односвязном списке, начиная с 0.
         * @return узел, находящийся на указанном индексе. Возвращает объект типа {@code Node<E>}, содержащий данные типа {@code E} и ссылку на следующий узел в односвязном списке.
         * @throws IndexOutOfBoundsException если индекс отрицательный или превышает размер списка.
         * @see Node
         */
        private Node<E> getByIndex(int index)
        {
            if (index < 0)
            {
                throw new IndexOutOfBoundsException("Index must be a positive number.");
            }

            Node<E> buffNode = head;
            for(int i = 0; i < index; i++)
            {
                if (buffNode.next == null)
                {
                    throw new IndexOutOfBoundsException("Index [" + index + "] out of list.");
                }
                buffNode = buffNode.next;
            }
            return buffNode;
        }
    }
    """

    funcs = parser.parse_content(java_code)
    assert len(funcs) == 1

    f = funcs[0]
    assert f.name == "getByIndex"
    assert f.qualified_name == "LinkedList.getByIndex"
    assert f.return_type == "Node<E>"
    assert f.parameters == ["int index"]
    assert f.visibility == "private"
    assert f.has_body is True

    expected_docstring = (
        "Получает узел по указанному индексу.\n\n"
        "@param index индекс узла, который нужно получить. "
        "Индекс должен быть неотрицательным и соответствовать позиции узла в односвязном списке, начиная с 0.\n"
        "@return узел, находящийся на указанном индексе. "
        "Возвращает объект типа {@code Node<E>}, содержащий данные типа {@code E} и ссылку на следующий узел в односвязном списке.\n"
        "@throws IndexOutOfBoundsException если индекс отрицательный или превышает размер списка.\n"
        "@see Node"
    )
    assert f.docstring == expected_docstring
