"""Distributed Transaction Manager with 2PC/3PC support"""
import time
import threading
import logging
from typing import Dict, List, Optional
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    INIT = "init"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ABORTING = "aborting"
    ABORTED = "aborted"
    TIMEOUT = "timeout"

class TransactionManager:
    """Manages distributed transactions using 2PC protocol"""
    
    def __init__(self, config: Dict):
        self.protocol = config.get('protocol', '2pc')  # 2pc or 3pc
        self.timeout = config.get('timeout', 30)
        self.coordinator_role = config.get('coordinator_role', 'primary')
        
        # Active transactions
        self.transactions = {}
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'total': 0,
            'committed': 0,
            'aborted': 0,
            'timeout': 0
        }
        
        logger.info(f"Transaction manager initialized with {self.protocol} protocol")
    
    def execute_transaction(self, transaction_id: str, operations: List[Dict]) -> Dict:
        """Execute a distributed transaction"""
        start_time = time.time()
        
        with self.lock:
            self.transactions[transaction_id] = {
                'status': TransactionStatus.INIT,
                'operations': operations,
                'participants': self._extract_participants(operations),
                'votes': {},
                'start_time': start_time
            }
            self.stats['total'] += 1
        
        try:
            # Phase 1: Prepare
            result = self._prepare_phase(transaction_id)
            
            if result['all_prepared']:
                # Phase 2: Commit
                result = self._commit_phase(transaction_id)
                if result['committed']:
                    with self.lock:
                        self.transactions[transaction_id]['status'] = TransactionStatus.COMMITTED
                        self.stats['committed'] += 1
                else:
                    with self.lock:
                        self.transactions[transaction_id]['status'] = TransactionStatus.ABORTED
                        self.stats['aborted'] += 1
            else:
                # Abort transaction
                self._abort_phase(transaction_id)
                with self.lock:
                    self.transactions[transaction_id]['status'] = TransactionStatus.ABORTED
                    self.stats['aborted'] += 1
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                'status': self.transactions[transaction_id]['status'].value,
                'message': result.get('message', ''),
                'latency_ms': latency_ms
            }
            
        except Exception as e:
            logger.error(f"Transaction {transaction_id} failed: {e}", exc_info=True)
            self._abort_phase(transaction_id)
            with self.lock:
                if transaction_id in self.transactions:
                    self.transactions[transaction_id]['status'] = TransactionStatus.ABORTED
                    self.stats['aborted'] += 1
            
            return {
                'status': 'aborted',
                'message': str(e),
                'latency_ms': (time.time() - start_time) * 1000
            }
    
    def _extract_participants(self, operations: List[Dict]) -> List[str]:
        """Extract participant node IDs from operations"""
        return list(set(op.get('node_id') for op in operations if op.get('node_id')))
    
    def _prepare_phase(self, transaction_id: str) -> Dict:
        """Phase 1: Prepare - send prepare messages to all participants"""
        with self.lock:
            txn = self.transactions[transaction_id]
            txn['status'] = TransactionStatus.PREPARING
        
        participants = txn['participants']
        votes = {}
        
        # Send prepare to all participants
        for participant_id in participants:
            try:
                # TODO: Send actual gRPC prepare message
                # For now, simulate
                vote = self._send_prepare(participant_id, transaction_id, txn['operations'])
                votes[participant_id] = vote
            except Exception as e:
                logger.error(f"Failed to send prepare to {participant_id}: {e}")
                votes[participant_id] = False
        
        with self.lock:
            txn['votes'] = votes
            all_prepared = all(votes.values()) and len(votes) == len(participants)
            
            if all_prepared:
                txn['status'] = TransactionStatus.PREPARED
        
        return {
            'all_prepared': all_prepared,
            'votes': votes
        }
    
    def _commit_phase(self, transaction_id: str) -> Dict:
        """Phase 2: Commit - send commit messages to all participants"""
        with self.lock:
            txn = self.transactions[transaction_id]
            txn['status'] = TransactionStatus.COMMITTING
        
        participants = txn['participants']
        acks = {}
        
        # Send commit to all participants
        for participant_id in participants:
            try:
                # TODO: Send actual gRPC commit message
                ack = self._send_commit(participant_id, transaction_id, commit=True)
                acks[participant_id] = ack
            except Exception as e:
                logger.error(f"Failed to send commit to {participant_id}: {e}")
                acks[participant_id] = False
        
        with self.lock:
            committed = all(acks.values()) and len(acks) == len(participants)
            if committed:
                txn['status'] = TransactionStatus.COMMITTED
        
        return {
            'committed': committed,
            'acks': acks
        }
    
    def _abort_phase(self, transaction_id: str):
        """Abort transaction - send abort to all participants"""
        with self.lock:
            if transaction_id not in self.transactions:
                return
            
            txn = self.transactions[transaction_id]
            txn['status'] = TransactionStatus.ABORTING
        
        participants = txn.get('participants', [])
        
        for participant_id in participants:
            try:
                # TODO: Send actual gRPC abort message
                self._send_commit(participant_id, transaction_id, commit=False)
            except Exception as e:
                logger.error(f"Failed to send abort to {participant_id}: {e}")
        
        with self.lock:
            txn['status'] = TransactionStatus.ABORTED
    
    def _send_prepare(self, participant_id: str, transaction_id: str, operations: List[Dict]) -> bool:
        """Send prepare message to participant (simulated)"""
        # TODO: Implement actual gRPC call
        time.sleep(0.05)  # Simulate network latency
        # Simulate: 95% success rate
        import random
        return random.random() > 0.05
    
    def _send_commit(self, participant_id: str, transaction_id: str, commit: bool) -> bool:
        """Send commit/abort message to participant (simulated)"""
        # TODO: Implement actual gRPC call
        time.sleep(0.03)  # Simulate network latency
        return True
    
    def get_statistics(self) -> Dict:
        """Get transaction statistics"""
        with self.lock:
            return {
                'total': self.stats['total'],
                'committed': self.stats['committed'],
                'aborted': self.stats['aborted'],
                'timeout': self.stats['timeout'],
                'commit_rate': (self.stats['committed'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0,
                'active_transactions': len([t for t in self.transactions.values() if t['status'] in [TransactionStatus.PREPARING, TransactionStatus.COMMITTING]])
            }
