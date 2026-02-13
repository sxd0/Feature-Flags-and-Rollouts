from __future__ import annotations

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Environment(Base):
    __tablename__ = "environments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)

    flag_states: Mapped[list[FeatureFlagState]] = relationship(
        back_populates="environment",
        cascade="all, delete-orphan",
    )


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)

    states: Mapped[list[FeatureFlagState]] = relationship(
        back_populates="flag",
        cascade="all, delete-orphan",
    )


class FeatureFlagState(Base):
    __tablename__ = "feature_flag_states"
    __table_args__ = (
        UniqueConstraint("flag_id", "environment_id", name="uq_flag_env"),
        CheckConstraint(
            "rollout_percentage >= 0 AND rollout_percentage <= 100", name="ck_rollout_pct"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    flag_id: Mapped[int] = mapped_column(
        ForeignKey("feature_flags.id", ondelete="CASCADE"), nullable=False
    )
    environment_id: Mapped[int] = mapped_column(
        ForeignKey("environments.id", ondelete="CASCADE"), nullable=False
    )

    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rollout_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    flag: Mapped[FeatureFlag] = relationship(back_populates="states")
    environment: Mapped[Environment] = relationship(back_populates="flag_states")
