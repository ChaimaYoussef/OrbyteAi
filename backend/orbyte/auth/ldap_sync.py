"""LDAP and Active Directory Group Synchronization Module for Orbyte.

Maps Active Directory / LDAP groups to Orbyte UserGroups and roles automatically.
Allows fully offline/air-gapped enterprise identity integration.
"""

from dataclasses import dataclass
from typing import Dict, List, Set
from uuid import UUID

from sqlalchemy.orm import Session

from orbyte.db.models import User, UserGroup, User__UserGroup
from orbyte.utils.logger import setup_logger

logger = setup_logger()


@dataclass
class ADGroupMapping:
    ad_group_dn: str
    orbyte_group_name: str
    is_curator: bool = False


class LDAPGroupSyncManager:
    """Manages synchronization between Active Directory/LDAP groups and Orbyte UserGroups."""

    def __init__(self, mappings: List[ADGroupMapping] | None = None):
        self.mappings = mappings or []

    def sync_user_groups_from_ad(
        self,
        db_session: Session,
        user: User,
        user_ad_group_dns: List[str],
    ) -> List[str]:
        """Synchronizes an authenticated user's Orbyte UserGroups based on their LDAP/AD groups.

        Args:
            db_session: SQLAlchemy session
            user: Target Orbyte User
            user_ad_group_dns: List of Distinguished Names (DNs) of AD groups the user belongs to.

        Returns:
            List of names of Orbyte UserGroups assigned to the user.
        """
        assigned_group_names: List[str] = []
        user_ad_set = {dn.lower() for dn in user_ad_group_dns}

        for mapping in self.mappings:
            if mapping.ad_group_dn.lower() in user_ad_set:
                # Find or get existing Orbyte UserGroup
                user_group = (
                    db_session.query(UserGroup)
                    .filter(UserGroup.name == mapping.orbyte_group_name)
                    .first()
                )

                if not user_group:
                    logger.info(
                        f"Creating new Orbyte UserGroup '{mapping.orbyte_group_name}' from AD sync."
                    )
                    user_group = UserGroup(name=mapping.orbyte_group_name)
                    db_session.add(user_group)
                    db_session.flush()

                # Check if membership already exists
                membership = (
                    db_session.query(User__UserGroup)
                    .filter(
                        User__UserGroup.user_id == user.id,
                        User__UserGroup.user_group_id == user_group.id,
                    )
                    .first()
                )

                if not membership:
                    logger.info(
                        f"Adding user {user.email} to group '{user_group.name}' (Curator={mapping.is_curator})."
                    )
                    membership = User__UserGroup(
                        user_id=user.id,
                        user_group_id=user_group.id,
                        is_curator=mapping.is_curator,
                    )
                    db_session.add(membership)
                else:
                    # Update curator status if changed
                    if membership.is_curator != mapping.is_curator:
                        membership.is_curator = mapping.is_curator

                assigned_group_names.append(user_group.name)

        db_session.commit()
        return assigned_group_names
