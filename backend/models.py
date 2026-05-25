from sqlalchemy import String, Integer, Float, ForeignKey, BigInteger, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True) 
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    
    children: Mapped[list["Child"]] = relationship(back_populates="parent")
    # Relation ajoutée pour accéder aux scans du parent
    scans: Mapped[list["ScanHistory"]] = relationship(back_populates="parent")

class Child(Base):
    __tablename__ = "enfants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    birthdate: Mapped[date] = mapped_column(Date, nullable=False)
    allergies: Mapped[str] = mapped_column(String, nullable=True, default="")

    id_parent: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id"))
    parent: Mapped["User"] = relationship(back_populates="children")

    stories: Mapped[list["Story"]] = relationship(back_populates="child")
    # L'enfant est maintenant lié à ses scans (historique)
    scans: Mapped[list["ScanHistory"]] = relationship(back_populates="child")

class Product(Base):
    __tablename__ = "produits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    barcode: Mapped[int] = mapped_column(BigInteger, index=True)
    
    type: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, nullable=False)
    brand: Mapped[str] = mapped_column(String, nullable=False)

    calories: Mapped[float] = mapped_column(Float)
    glucides: Mapped[float] = mapped_column(Float, default=0.0)
    sugars: Mapped[float] = mapped_column(Float, default=0.0)
    fibers: Mapped[float] = mapped_column(Float, default=0.0)
    
    calcium: Mapped[float] = mapped_column(Float)
    proteins: Mapped[float] = mapped_column(Float)
    lipids: Mapped[float] = mapped_column(Float)
    salt: Mapped[float] = mapped_column(Float)

    # Le produit est lié à l'historique des scans
    scans: Mapped[list["ScanHistory"]] = relationship(back_populates="product")

class ScanHistory(Base):
    __tablename__ = "historique_scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scan_date: Mapped[date] = mapped_column(Date, default=date.today)

    # Clés étrangères créant le cloisonnement parfait
    id_parent: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id"))
    id_child: Mapped[int] = mapped_column(ForeignKey("enfants.id"))
    id_product: Mapped[int] = mapped_column(ForeignKey("produits.id"))

    # Relations
    parent: Mapped["User"] = relationship(back_populates="scans")
    child: Mapped["Child"] = relationship(back_populates="scans")
    product: Mapped["Product"] = relationship(back_populates="scans")

class Story(Base):
    __tablename__ = "histoires"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url_mp3: Mapped[str] = mapped_column(String, nullable=False)
    script: Mapped[str] = mapped_column(String, nullable=False)

    id_child: Mapped[int] = mapped_column(ForeignKey("enfants.id"))
    child: Mapped["Child"] = relationship(back_populates="stories")