from sqlalchemy import String, Integer, Float, ForeignKey, BigInteger, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True) # Ajout du username unique
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    
    children: Mapped[list["Child"]] = relationship(back_populates="parent")

class Child(Base):
    __tablename__ = "enfants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    # Remplacement de age par birthdate
    birthdate: Mapped[date] = mapped_column(Date, nullable=False)
    # Ajout de la colonne allergies
    allergies: Mapped[str] = mapped_column(String, nullable=True, default="")

    id_parent: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id"))
    parent: Mapped["User"] = relationship(back_populates="children")

    products: Mapped[list["Product"]] = relationship(back_populates="child")
    stories: Mapped[list["Story"]] = relationship(back_populates="child")

class Product(Base):
    __tablename__ = "produits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    barcode: Mapped[int] = mapped_column(BigInteger, index=True)
    
    type: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, nullable=False)
    brand: Mapped[str] = mapped_column(String, nullable=False)

    calories: Mapped[float] = mapped_column(Float)
    glucides: Mapped[float] = mapped_column(Float, default=0.0)
    # AJOUT DES DEUX CHAMPS DEMANDÉS
    sugars: Mapped[float] = mapped_column(Float, default=0.0)
    fibers: Mapped[float] = mapped_column(Float, default=0.0)
    
    calcium: Mapped[float] = mapped_column(Float)
    proteins: Mapped[float] = mapped_column(Float)
    lipids: Mapped[float] = mapped_column(Float)
    salt: Mapped[float] = mapped_column(Float)

    id_child: Mapped[int] = mapped_column(ForeignKey("enfants.id"))
    child: Mapped["Child"] = relationship(back_populates="products")

class Story(Base):
    __tablename__ = "histoires"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url_mp3: Mapped[str] = mapped_column(String, nullable=False)
    script: Mapped[str] = mapped_column(String, nullable=False)

    id_child: Mapped[int] = mapped_column(ForeignKey("enfants.id"))
    child: Mapped["Child"] = relationship(back_populates="stories")